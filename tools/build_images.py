"""Find a freely licensed photo on Wikimedia Commons for every Earth and USA place, and write ../images.js.

Usage: python -I build_images.py

It reads data.js and usa.js, looks each place up on English Wikipedia, takes the Wikidata image (or the Wikivoyage
banner, or the article's lead image), and keeps only photos under CC0, CC BY, CC BY-SA or in the public domain.
The game stores just the address and the credit; players' browsers load the picture from Wikimedia.
"""
import hashlib
import html
import json
import pathlib
import re
import time
import urllib.parse
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).parent.parent
OUT = ROOT / "images.js"
AGENT = "Mapolo-build/1.0 (geography quiz; one-off image lookup)"
WIDTH = 500  # one of Wikimedia's standard thumbnail widths
FREE = re.compile(r"^(cc0|cc[ -]by(-sa)?( \d(\.\d)?)?.*|public domain|pd.*)$", re.I)
KEYWORDS = {
    "country": r"country|state|island|kingdom|republic|nation|territory|archipelago|principality|sultanate|emirate|federation",
    "capital": r"city|capital|town|municipality|village|commune|district|seat|community|metropolis|settlement|atoll",
    "mountain": r"mountain|peak|volcano|summit|massif|hill|dome|monolith|monument|memorial|point",
    "river": r"river|waterway|stream|tributary",
    "state": r"state",
}
# Article titles where the plain name finds the wrong page.
TITLES = {
    ("earth", "country", "Georgia"): "Georgia (country)",
    ("earth", "country", "Micronesia"): "Federated States of Micronesia",
    ("earth", "country", "Palestine"): "State of Palestine",
    ("earth", "river", "Thames"): "River Thames",
    ("earth", "river", "Don"): "Don (river)",
    ("earth", "river", "Po"): "Po (river)",
    ("usa", "state", "Georgia"): "Georgia (U.S. state)",
    ("usa", "state", "Washington"): "Washington (state)",
    ("usa", "state", "New York"): "New York (state)",
    ("usa", "river", "Red River"): "Red River of the South",
    ("usa", "river", "Green"): "Green River (Colorado River tributary)",
}


CACHE = pathlib.Path(__file__).parent / ".image-cache"


def get(url, params):
    """Fetches JSON politely: answers are cached on disk, and a busy server's Retry-After is respected."""
    address = f"{url}?{urllib.parse.urlencode(params)}"
    cached = CACHE / (hashlib.sha256(address.encode()).hexdigest() + ".json")
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf8"))
    request = urllib.request.Request(address, headers={"User-Agent": AGENT})
    for attempt in range(6):
        time.sleep(1)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.load(response)
            CACHE.mkdir(exist_ok=True)
            cached.write_text(json.dumps(data), encoding="utf8")
            return data
        except urllib.error.HTTPError as error:
            wait = int(error.headers.get("Retry-After") or 0) or 15 * (attempt + 1)
            print(f"{error.code}, waiting {wait} s")
            time.sleep(min(wait, 300))
        except OSError as error:
            print("retrying after", error)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"gave up on {url}")


def load_js(name):
    text = (ROOT / name).read_text(encoding="utf8")
    return json.loads(text[text.index("{"): text.rindex("}") + 1])


def places():
    """(world, kind, name, title candidates) for every place that can have a picture."""
    earth, usa = load_js("data.js"), load_js("usa.js")
    out = []
    for c in earth["countries"]:
        out.append(("earth", "country", c["name"], [c["name"]]))
        if c["capital"]:
            out.append(("earth", "capital", c["capital"], [c["capital"], f"{c['capital']}, {c['name']}"]))
    for m in earth["mountains"]:
        out.append(("earth", "mountain", m["name"], [m["name"], f"{m['name']} (mountain)", f"{m['name']} (volcano)"]))
    for r in earth["rivers"]:
        out.append(("earth", "river", r["name"], river_titles(r["name"])))
    for s in usa["states"]:
        out.append(("usa", "state", s["en"], [s["en"]]))
        c = s["capital"]["en"]
        out.append(("usa", "capital", c, [f"{c}, {s['en']}", c]))
    for m in usa["mountains"]:
        out.append(("usa", "mountain", m["en"], [m["en"], f"{m['en']} (mountain)"]))
    for r in usa["rivers"]:
        out.append(("usa", "river", r["en"], river_titles(r["en"])))
    return [(w, k, n, [TITLES[(w, k, n)]] if (w, k, n) in TITLES else titles) for w, k, n, titles in out]


def river_titles(name):
    if name.endswith("River"):
        return [name]
    return [f"{name} River", f"River {name}", f"{name} (river)", name]


def look_up(titles):
    """Wikipedia pages for up to 50 titles: {asked title: page}, following redirects."""
    data = get("https://en.wikipedia.org/w/api.php", {
        "action": "query", "format": "json", "formatversion": 2, "redirects": 1, "titles": "|".join(titles),
        "prop": "pageprops|pageimages|description", "ppprop": "wikibase_item|disambiguation", "piprop": "name"})
    query = data["query"]
    hops = {n["from"]: n["to"] for n in query.get("normalized", [])}
    hops.update({r["from"]: r["to"] for r in query.get("redirects", [])})
    pages = {p["title"]: p for p in query["pages"]}
    found = {}
    for title in titles:
        final = title
        for _ in range(3):
            final = hops.get(final, final)
        found[title] = pages.get(final)
    return found


def resolve(items):
    """Picks the first title per place whose page exists, isn't a disambiguation and is about the right kind of thing."""
    chosen, pending = {}, list(items)
    for round_ in range(5):
        asks = [(item, item[3][round_]) for item in pending if round_ < len(item[3])]
        pending = []
        for start in range(0, len(asks), 50):
            batch = asks[start:start + 50]
            pages = look_up([t for _, t in batch])
            for item, title in batch:
                page = pages.get(title)
                ok = (page and not page.get("missing") and "disambiguation" not in page.get("pageprops", {})
                      and re.search(KEYWORDS[item[1]], page.get("description", "") or "", re.I))
                if ok:
                    chosen[item[:3]] = page
                else:
                    pending.append(item)
            time.sleep(.3)
    for item in pending:
        print("no article:", item[:3])
    return chosen


def wikidata_images(ids):
    """Wikidata image (P18) and Wikivoyage banner (P948) file names for each item."""
    out = {}
    for start in range(0, len(ids), 150):
        values = " ".join(f"wd:{i}" for i in ids[start:start + 150])
        query = f"SELECT ?item ?image ?banner WHERE {{ VALUES ?item {{ {values} }} OPTIONAL {{ ?item wdt:P18 ?image }} OPTIONAL {{ ?item wdt:P948 ?banner }} }}"
        data = get("https://query.wikidata.org/sparql", {"query": query, "format": "json"})
        for row in data["results"]["bindings"]:
            qid = row["item"]["value"].rsplit("/", 1)[1]
            entry = out.setdefault(qid, {"image": [], "banner": []})
            for key in ("image", "banner"):
                if key in row:
                    name = urllib.parse.unquote(row[key]["value"].rsplit("/", 1)[1]).replace("_", " ")
                    if name not in entry[key]:
                        entry[key].append(name)
        time.sleep(1)
    return out


def state_flags(qids):
    """Wikidata flag (P41) file names for the US states, which the game has no flag files for."""
    values = " ".join(f"wd:{i}" for i in qids)
    data = get("https://query.wikidata.org/sparql", {"query": f"SELECT ?item ?flag WHERE {{ VALUES ?item {{ {values} }} ?item wdt:P41 ?flag }}", "format": "json"})
    out = {}
    for row in data["results"]["bindings"]:
        out.setdefault(row["item"]["value"].rsplit("/", 1)[1], urllib.parse.unquote(row["flag"]["value"].rsplit("/", 1)[1]).replace("_", " "))
    return out


def file_info(names, width=WIDTH):
    """Thumbnail address, size, author and license for Commons files."""
    out = {}
    names = sorted(set(names))
    for start in range(0, len(names), 20):
        data = get("https://commons.wikimedia.org/w/api.php", {
            "action": "query", "format": "json", "formatversion": 2, "titles": "|".join(f"File:{n}" for n in names[start:start + 20]),
            "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": width})
        hops = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
        for page in data["query"]["pages"]:
            info = (page.get("imageinfo") or [None])[0]
            if not info:
                continue
            meta = info.get("extmetadata", {})
            license_ = meta.get("LicenseShortName", {}).get("value", "")
            artist = html.unescape(re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", ""))).strip()
            asked = hops.get(page["title"], page["title"])[5:]
            # Drop tracking parameters from the address, and web links from the credit.
            artist = re.sub(r"https?://\S+", "", artist).strip(" ,;-")
            out[asked] = {"src": (info.get("thumburl") or info["url"]).split("?")[0], "w": info.get("thumbwidth") or info["width"],
                          "h": info.get("thumbheight") or info["height"], "by": re.sub(r"\s+", " ", artist)[:80] or "Unknown",
                          "license": license_, "free": bool(FREE.match(license_.strip())) and "nc" not in license_.lower() and "nd" not in license_.lower().split("-")}
        time.sleep(.3)
    return out


def main():
    items = places()
    print(len(items), "places")
    pages = resolve(items)
    ids = sorted({p["pageprops"]["wikibase_item"] for p in pages.values() if "wikibase_item" in p.get("pageprops", {})})
    wikidata = wikidata_images(ids)
    candidates = {}
    for key, page in pages.items():
        qid = page.get("pageprops", {}).get("wikibase_item")
        found = wikidata.get(qid, {"image": [], "banner": []})
        lead = [page["pageimage"].replace("_", " ")] if page.get("pageimage") else []
        # Photos only: drawings, maps, flags and coats of arms are almost always SVG or PNG.
        candidates[key] = [n for n in found["image"] + found["banner"] + lead if n.lower().endswith((".jpg", ".jpeg"))]
    info = file_info([n for names in candidates.values() for n in names])
    result, missing = {}, []
    for (world, kind, name), names in candidates.items():
        pick = next((info[n] for n in names if n in info and info[n]["free"]), None)
        if not pick:
            missing.append((world, kind, name))
            continue
        bucket = result.setdefault(world, {}).setdefault("country" if kind == "state" else kind, {})
        bucket[name] = {k: pick[k] for k in ("src", "w", "h", "by", "license")}
    # State flags are almost all in the public domain. Only those are used, so they need no credit line.
    states = {name: pages[("usa", "state", name)]["pageprops"]["wikibase_item"] for (world, kind, name) in pages if kind == "state"}
    flags = state_flags(sorted(states.values()))
    flag_info = file_info(list(flags.values()), width=250)
    for name, qid in states.items():
        info = flag_info.get(flags.get(qid))
        if info and re.match(r"public domain|pd|cc0", info["license"], re.I):
            result["usa"].setdefault("flag", {})[name] = {k: info[k] for k in ("src", "w", "h")}
        else:
            print("no public-domain flag:", name)
    print(len(result["usa"].get("flag", {})), "state flags")
    total = sum(len(b) for w in result.values() for k, b in w.items() if k != "flag")
    print(f"{total} pictures, {len(missing)} places without one")
    for m in missing:
        print("no free photo:", m)
    OUT.write_text("/* Generated by tools/build_images.py: one freely licensed Wikimedia Commons photo per place, with its credit. */\n"
                   f"window.BLANK_MAP_IMAGES = {json.dumps(result, ensure_ascii=False, separators=(',', ':'))};\n", encoding="utf8")
    print("wrote", OUT, OUT.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
