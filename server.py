"""Serves Blank Map and keeps player profiles in SQLite. Uses only the Python standard library."""
import argparse
import contextlib
import hashlib
import hmac
import json
import math
import os
import pathlib
import re
import secrets
import signal
import sqlite3
import sys
import threading
import time
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent
STATIC = {"/": "index.html", "/index.html": "index.html", "/data.js": "data.js", "/facts.js": "facts.js", "/quiz.js": "quiz.js",
          "/middleearth.js": "middleearth.js"}
FLAG_PATH = re.compile(r"/flags/[a-z]{2}\.svg")
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml"}

COOKIE = "blank_map_session"
SESSION_SECONDS = 90 * 24 * 3600
MAX_BODY = 4096
NAME_LENGTH = (2, 24)
PASSWORD_LENGTH = (6, 200)
SCRYPT = {"n": 2 ** 14, "r": 8, "p": 1}
ATTEMPT_LIMIT, ATTEMPT_SECONDS = 20, 300

# What each map can ask about. Areas are the "Where" choices, regions are where a place actually is.
WORLDS = {
    "earth": {
        "kinds": ("country", "capital", "flag", "mountain", "river"),
        "regions": ("Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Antarctica"),
        "root": "World",
    },
    "middle": {
        "kinds": ("country", "capital", "mountain", "river"),
        "regions": ("Eriador", "Rhovanion", "Southlands"),
        "root": "Middle-earth",
    },
}
LEVELS = ("easy", "medium", "hard")
MODES = ("name", "find")
ROUND_ID = re.compile(r"[0-9a-f]{32}")

# Accuracy looks at the latest answers only, and each answer counts a little less than the one after it.
# Older answers fall out of the window entirely, so a run of perfect answers always reaches exactly 100%.
WINDOW = 30
DECAY = 0.93

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  name_key TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS answers (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  round_id TEXT NOT NULL,
  at INTEGER NOT NULL,
  kind TEXT NOT NULL,
  region TEXT NOT NULL,
  area TEXT NOT NULL,
  level TEXT NOT NULL,
  mode TEXT NOT NULL,
  place TEXT NOT NULL,
  points INTEGER NOT NULL,
  world TEXT NOT NULL DEFAULT 'earth'
);
CREATE INDEX IF NOT EXISTS answers_by_user ON answers (user_id, id);
"""


def hash_password(password):
    salt = secrets.token_bytes(16)
    key = hashlib.scrypt(password.encode(), salt=salt, **SCRYPT)
    return f"scrypt${SCRYPT['n']}${SCRYPT['r']}${SCRYPT['p']}${salt.hex()}${key.hex()}"


def check_password(password, stored):
    _, n, r, p, salt, key = stored.split("$")
    found = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p))
    return hmac.compare_digest(found, bytes.fromhex(key))


# Checked when a name doesn't exist, so a wrong name takes as long as a wrong password.
DUMMY_HASH = hash_password(secrets.token_hex(16))


def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def clean_name(name):
    return " ".join(unicodedata.normalize("NFKC", name).split())


def accuracy(points):
    """Takes points newest first and returns a whole percent. It rounds down, so 100 always means all perfect."""
    recent = points[:WINDOW]
    weights = [DECAY ** age for age in range(len(recent))]
    return math.floor(round(sum(p * w for p, w in zip(recent, weights)) / sum(weights), 6))


def stat(points):
    return {"score": accuracy(points) if points else None, "count": len(points)}


class Attempts:
    """Counts login failures and new profiles per address, to slow down password guessing."""

    def __init__(self):
        self.lock = threading.Lock()
        self.seen = {}

    def _recent(self, address, now):
        return [t for t in self.seen.get(address, []) if now - t < ATTEMPT_SECONDS]

    def blocked(self, address):
        with self.lock:
            return len(self._recent(address, time.time())) >= ATTEMPT_LIMIT

    def add(self, address):
        now = time.time()
        with self.lock:
            self.seen = {a: kept for a in self.seen if (kept := self._recent(a, now))}
            self.seen.setdefault(address, []).append(now)


class Game(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, db_path, secure_cookie):
        super().__init__(address, Handler)
        self.db_path = db_path
        self.secure_cookie = secure_cookie
        self.attempts = Attempts()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.executescript(SCHEMA)
            # Databases from before Middle-earth only hold Earth answers.
            if "world" not in [row[1] for row in con.execute("PRAGMA table_info(answers)")]:
                con.execute("ALTER TABLE answers ADD COLUMN world TEXT NOT NULL DEFAULT 'earth'")

    @contextlib.contextmanager
    def db(self):
        con = sqlite3.connect(self.db_path, timeout=10)
        try:
            con.row_factory = sqlite3.Row
            con.execute("PRAGMA foreign_keys=ON")
            with con:
                yield con
        finally:
            con.close()


class Handler(BaseHTTPRequestHandler):
    server_version = "BlankMap"
    sys_version = ""
    timeout = 30

    def send_body(self, status, body, content_type, headers=()):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store" if content_type == "application/json" else "no-cache")
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_json(self, status, data, headers=()):
        self.send_body(status, json.dumps(data).encode(), "application/json", headers)

    def fail(self, status, code):
        self.send_json(status, {"error": code})

    def session_cookie(self, value, max_age):
        secure = "; Secure" if self.server.secure_cookie else ""
        return "Set-Cookie", f"{COOKIE}={value}; Path=/; Max-Age={max_age}; HttpOnly; SameSite=Strict{secure}"

    def session_token(self):
        for part in self.headers.get("Cookie", "").split(";"):
            name, _, value = part.strip().partition("=")
            if name == COOKIE:
                return value
        return None

    def current_user(self, con):
        token = self.session_token()
        if not token:
            return None
        return con.execute(
            "SELECT users.* FROM sessions JOIN users ON users.id = sessions.user_id WHERE token_hash = ? AND expires > ?",
            (hash_token(token), int(time.time())),
        ).fetchone()

    def read_json(self):
        """Returns the request's JSON object, or None after answering with an error.
        Requiring the JSON content type also stops other sites posting here from a plain form."""
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.fail(415, "type")
            return None
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.fail(400, "body")
            return None
        if not 0 <= length <= MAX_BODY:
            self.fail(413, "body")
            return None
        try:
            data = json.loads(self.rfile.read(length))
        except ValueError:
            self.fail(400, "body")
            return None
        if not isinstance(data, dict):
            self.fail(400, "body")
            return None
        return data

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/me":
            return self.get_me()
        if path == "/api/profile":
            return self.get_profile()
        name = STATIC.get(path) or (path[1:] if FLAG_PATH.fullmatch(path) else None)
        target = ROOT / name if name else None
        if not target or not target.is_file():
            return self.send_body(404, b"Not found", "text/plain; charset=utf-8")
        self.send_body(200, target.read_bytes(), TYPES[target.suffix])

    do_HEAD = do_GET

    def do_POST(self):
        routes = {"/api/register": self.post_register, "/api/login": self.post_login,
                  "/api/logout": self.post_logout, "/api/answers": self.post_answer}
        route = routes.get(self.path)
        if not route:
            return self.fail(404, "missing")
        data = self.read_json()
        if data is not None:
            route(data)

    def get_me(self):
        with self.server.db() as con:
            user = self.current_user(con)
        self.send_json(200, {"user": {"name": user["name"]} if user else None})

    def start_session(self, con, user_id):
        token = secrets.token_urlsafe(32)
        now = int(time.time())
        con.execute("DELETE FROM sessions WHERE expires <= ?", (now,))
        con.execute("INSERT INTO sessions (token_hash, user_id, expires) VALUES (?, ?, ?)",
                    (hash_token(token), user_id, now + SESSION_SECONDS))
        return self.session_cookie(token, SESSION_SECONDS)

    def post_register(self, data):
        address = self.client_address[0]
        name, password = data.get("name"), data.get("password")
        if not isinstance(name, str) or not isinstance(password, str):
            return self.fail(400, "body")
        name = clean_name(name)
        if not NAME_LENGTH[0] <= len(name) <= NAME_LENGTH[1] or not name.isprintable():
            return self.fail(400, "name")
        if not PASSWORD_LENGTH[0] <= len(password) <= PASSWORD_LENGTH[1]:
            return self.fail(400, "password")
        if self.server.attempts.blocked(address):
            return self.fail(429, "limit")
        self.server.attempts.add(address)
        password_hash = hash_password(password)
        try:
            with self.server.db() as con:
                user_id = con.execute("INSERT INTO users (name, name_key, password_hash, created) VALUES (?, ?, ?, ?)",
                                      (name, name.casefold(), password_hash, int(time.time()))).lastrowid
                cookie = self.start_session(con, user_id)
        except sqlite3.IntegrityError:
            return self.fail(409, "taken")
        self.send_json(201, {"user": {"name": name}}, [cookie])

    def post_login(self, data):
        address = self.client_address[0]
        name, password = data.get("name"), data.get("password")
        if not isinstance(name, str) or not isinstance(password, str) or len(password) > PASSWORD_LENGTH[1]:
            return self.fail(401, "wrong")
        if self.server.attempts.blocked(address):
            return self.fail(429, "limit")
        with self.server.db() as con:
            user = con.execute("SELECT * FROM users WHERE name_key = ?", (clean_name(name).casefold(),)).fetchone()
        matches = check_password(password, user["password_hash"] if user else DUMMY_HASH)
        if not user or not matches:
            self.server.attempts.add(address)
            return self.fail(401, "wrong")
        with self.server.db() as con:
            cookie = self.start_session(con, user["id"])
        self.send_json(200, {"user": {"name": user["name"]}}, [cookie])

    def post_logout(self, _data):
        token = self.session_token()
        if token:
            with self.server.db() as con:
                con.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))
        self.send_json(200, {"user": None}, [self.session_cookie("", 0)])

    def post_answer(self, data):
        points = data.get("points")
        place = data.get("place")
        round_id = data.get("round")
        world = WORLDS.get(data.get("world", "earth"))
        valid = (world is not None and isinstance(points, int) and not isinstance(points, bool) and 0 <= points <= 100
                 and isinstance(place, str) and 0 < len(place) <= 80
                 and isinstance(round_id, str) and ROUND_ID.fullmatch(round_id)
                 and data.get("kind") in world["kinds"] and data.get("region") in world["regions"]
                 and data.get("area") in (world["root"], *world["regions"])
                 and data.get("level") in LEVELS and data.get("mode") in MODES)
        if not valid:
            return self.fail(400, "answer")
        with self.server.db() as con:
            user = self.current_user(con)
            if not user:
                return self.fail(401, "login")
            con.execute(
                "INSERT INTO answers (user_id, round_id, at, world, kind, region, area, level, mode, place, points) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user["id"], round_id, int(time.time()), data.get("world", "earth"), data["kind"], data["region"], data["area"], data["level"], data["mode"], place, points),
            )
        self.send_json(201, {"saved": True})

    def get_profile(self):
        with self.server.db() as con:
            user = self.current_user(con)
            if not user:
                return self.fail(401, "login")
            answers = con.execute("SELECT world, kind, region, points FROM answers WHERE user_id = ? ORDER BY id DESC", (user["id"],)).fetchall()
            rounds = con.execute(
                """SELECT MAX(at) AS at, MIN(world) AS world, MIN(area) AS area, MIN(level) AS level, GROUP_CONCAT(DISTINCT kind) AS kinds,
                          COUNT(*) AS answered, SUM(points) AS points
                   FROM answers WHERE user_id = ? GROUP BY round_id ORDER BY MAX(id) DESC LIMIT 10""",
                (user["id"],),
            ).fetchall()
        def world_stats(name, world):
            mine = [a for a in answers if a["world"] == name]
            return {
                "overall": stat([a["points"] for a in mine]),
                "kinds": {kind: stat([a["points"] for a in mine if a["kind"] == kind]) for kind in world["kinds"]},
                "regions": {region: stat([a["points"] for a in mine if a["region"] == region]) for region in world["regions"]},
            }
        self.send_json(200, {
            "name": user["name"],
            "overall": stat([a["points"] for a in answers]),
            "worlds": {name: world_stats(name, world) for name, world in WORLDS.items()},
            "rounds": [{**dict(r), "kinds": r["kinds"].split(",")} for r in rounds],
            "window": WINDOW,
        })


def main():
    parser = argparse.ArgumentParser(description="Serve Blank Map with player profiles.")
    parser.add_argument("--host", default=os.environ.get("BLANK_MAP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("BLANK_MAP_PORT", "8770")))
    parser.add_argument("--db", type=pathlib.Path, default=pathlib.Path(os.environ.get("BLANK_MAP_DB", ROOT / "userdata" / "blank-map.sqlite")))
    args = parser.parse_args()
    # Set this when the game sits behind HTTPS, so browsers never send the login cookie unencrypted.
    secure_cookie = os.environ.get("BLANK_MAP_SECURE_COOKIE") == "1"
    server = Game((args.host, args.port), args.db, secure_cookie)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    print(f"Blank Map is at http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
