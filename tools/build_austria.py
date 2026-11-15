"""Join tools/austria_content.py with map data and write ../austria.js.

Usage: python -I build_austria.py <dir with the downloads below>

- ne_10m_admin_1_states_provinces.geojson, ne_10m_admin_0_countries.geojson and ne_10m_lakes.geojson (Natural Earth, public domain)

Rivers and lakes come from OpenStreetMap (ODbL) through the Overpass API. The answers are saved next to the downloads
as osm_rivers.json and osm_lakes.json, so later runs work offline. Cities and peaks get their position, and peaks
their height, from Wikidata (CC0).
"""
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import austria_content as content  # noqa: E402
import build_images as wiki  # noqa: E402

RAW = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).parent.parent / "austria.js"
BOX = (46.3, 9.45, 49.05, 17.2)  # south, west, north, east
NEAR_BORDER = .02  # degrees: river points this close outside the border still count, for border rivers


def load(name):
    return json.loads((RAW / name).read_text(encoding="utf8"))


def facts(pairs):
    return [[en for en, _ in pairs], [de for _, de in pairs]]


def overpass(name, query):
    """Runs an Overpass query once and keeps the answer next to the downloads."""
    path = RAW / name
    if not path.exists():
        body = urllib.parse.urlencode({"data": query}).encode()
        request = urllib.request.Request("https://overpass-api.de/api/interpreter", body, headers={"User-Agent": wiki.AGENT})
        for attempt in range(6):
            try:
                with urllib.request.urlopen(request, timeout=300) as response:
                    path.write_bytes(response.read())
                break
            except OSError as error:
                # The public server is often busy; it asks for patience rather than a different query.
                print(f"Overpass: {error}, trying again in {30 * (attempt + 1)} s")
                time.sleep(30 * (attempt + 1))
        else:
            raise RuntimeError("Overpass kept failing")
    return json.loads(path.read_text(encoding="utf8"))


def simplify(points, tolerance):
    """Douglas-Peucker in degrees, which is plenty for a quiz map."""
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    length = (dx * dx + dy * dy) ** .5 or 1e-12
    far, index = 0, 0
    for i in range(1, len(points) - 1):
        x, y = points[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / length
        if d > far:
            far, index = d, i
    if far <= tolerance:
        return [points[0], points[-1]]
    return simplify(points[:index + 1], tolerance)[:-1] + simplify(points[index:], tolerance)


def rounded(points, digits=3):
    out = []
    for x, y in points:
        p = [round(x, digits), round(y, digits)]
        if not out or out[-1] != p:
            out.append(p)
    return out


# ---------- States ----------
by_ne = {entry[3]: name for name, entry in content.STATES.items()}
region_of = {state: region for region, states in content.REGIONS.items() for state in states}
shapes = {}
for f in load("ne_10m_admin_1_states_provinces.geojson")["features"]:
    p = f["properties"]
    if p["adm0_a3"] == "AUT":
        g = f["geometry"]
        polygons = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        shapes[by_ne[p["name"]]] = {"type": "MultiPolygon", "coordinates": [[rounded(ring) for ring in poly] for poly in polygons]}
assert set(shapes) == set(content.STATES), set(shapes) ^ set(content.STATES)
capital_of = {city[3]: name for name, city in content.CITIES.items() if city[4]}
states = [{"en": name, "de": de, "aliases": aliases, "tier": tier, "region": region_of[name], "capital": capital_of[name], "title": title,
           "geo": shapes[name], "facts": facts(f)} for name, (de, aliases, tier, _, title, f) in content.STATES.items()]

# The country's outline, for cutting rivers off at the border.
austria = next(f["geometry"] for f in load("ne_10m_admin_0_countries.geojson")["features"] if f["properties"]["ADM0_A3"] == "AUT")
outline = [ring for poly in ([austria["coordinates"]] if austria["type"] == "Polygon" else austria["coordinates"]) for ring in poly]


def inside(x, y):
    hit = False
    for ring in outline:
        for i in range(len(ring) - 1):
            (x1, y1), (x2, y2) = ring[i][:2], ring[i + 1][:2]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                hit = not hit
    return hit


def border_distance(x, y):
    best = 1e9
    for ring in outline:
        for i in range(len(ring) - 1):
            (x1, y1), (x2, y2) = ring[i][:2], ring[i + 1][:2]
            dx, dy = x2 - x1, y2 - y1
            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy or 1e-12)))
            best = min(best, ((x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2) ** .5)
    return best


def in_austria(x, y, margin=NEAR_BORDER):
    return inside(x, y) or border_distance(x, y) < margin


# ---------- Rivers ----------
def osm_names(names):
    return "|".join(n.replace("|", "") for n in names)


river_names = sorted({n for r in content.RIVERS.values() for n in r[4]})
# Border rivers carry both languages, like "March / Morava", so either half may match.
pattern = f"^({osm_names(river_names)})( / .*)?$|^.* / ({osm_names(river_names)})$"
osm = overpass("osm_rivers.json", f'[out:json][timeout:240];way["waterway"="river"]["name"~"{pattern}"]{BOX};out geom;')
ways = {}
for w in osm["elements"]:
    for part in w["tags"]["name"].split(" / "):
        ways.setdefault(part, []).append([[n["lon"], n["lat"]] for n in w["geometry"]])


def chain(lines):
    """Joins ways that meet end to start into longer lines, so a river isn't hundreds of short pieces."""
    lines = [l[:] for l in lines]
    joined = True
    while joined:
        joined = False
        for i, a in enumerate(lines):
            for j, b in enumerate(lines):
                if i != j and a[-1] == b[0]:
                    lines[i] = a + b[1:]
                    del lines[j]
                    joined = True
                    break
            if joined:
                break
    return lines


rivers = []
for name, (de, aliases, tier, region, names, title, f) in content.RIVERS.items():
    lines = []
    for line in chain([l for n in names for l in ways.get(n, [])]):
        run = []
        for x, y in simplify(line, .002):
            if in_austria(x, y):
                run.append([x, y])
            elif run:
                lines.append(run)
                run = []
        lines.append(run)
    lines = [rounded(l) for l in lines if len(l) > 1]
    assert lines, f"no river data for {name}"
    rivers.append({"en": name, "de": de, "aliases": aliases, "tier": tier, "region": region, "title": title, "lines": lines, "facts": facts(f)})
    print(f"{name}: {len(lines)} lines, {sum(len(l) for l in lines)} points")

# ---------- Lakes ----------
lake_names = sorted({l[4] for l in content.LAKES.values() if l[4]})
pattern = f"^({osm_names(lake_names)})( / .*)?$"
osm = overpass("osm_lakes.json", f'[out:json][timeout:240];(way["natural"="water"]["name"~"{pattern}"]{BOX};'
                                 f'relation["natural"="water"]["name"~"{pattern}"]{BOX};);out geom;')


def rings_of(element):
    """Outer rings of an OSM way or multipolygon relation, joining member ways into closed rings."""
    if element["type"] == "way":
        return [[[n["lon"], n["lat"]] for n in element["geometry"]]]
    parts = [[[n["lon"], n["lat"]] for n in m["geometry"]] for m in element["members"] if m.get("role") == "outer" and m.get("geometry")]
    rings = []
    while parts:
        ring = parts.pop()
        while ring[0] != ring[-1]:
            for i, p in enumerate(parts):
                if p[0] == ring[-1]:
                    ring += p[1:]
                elif p[-1] == ring[-1]:
                    ring += p[::-1][1:]
                else:
                    continue
                del parts[i]
                break
            else:
                break
        if ring[0] == ring[-1]:
            rings.append(ring)
    return rings


def ring_area(ring):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:]))) / 2


best = {}
for element in osm["elements"]:
    name = element["tags"]["name"].split(" / ")[0]
    for ring in rings_of(element):
        x, y = sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)
        if inside(x, y) and ring_area(ring) > ring_area(best.get(name, [[0, 0]] * 3)):
            best[name] = ring
for f in load("ne_10m_lakes.geojson")["features"]:
    if f["properties"].get("name") == "Bodensee":
        g = f["geometry"]
        best[None] = max([poly[0] for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"])], key=ring_area)

lakes = []
for name, (de, aliases, tier, region, osm_name, title, f) in content.LAKES.items():
    ring = best.get(osm_name)
    assert ring, f"no lake data for {name}"
    # A closed ring starts and ends on the same point, so it is simplified as two halves.
    points, half = [p[:2] for p in ring], len(ring) // 2
    shape = rounded(simplify(points[:half + 1], .0015) + simplify(points[half:], .0015)[1:], 4)
    lakes.append({"en": name, "de": de, "aliases": aliases, "tier": tier, "region": region, "title": title, "shape": [[shape]], "facts": facts(f)})
    print(f"{name}: {len(shape)} points")

# ---------- Cities and peaks, placed by Wikidata ----------
asks = ([("austria", "capital", n, [c[5], f"{c[5]}, Austria"]) for n, c in content.CITIES.items()]
        + [("austria", "mountain", n, [m[4], f"{m[4]} (mountain)", f"{m[4]} (Alps)", f"{m[4]} (Austria)"]) for n, m in content.MOUNTAINS.items()])
pages = wiki.resolve(asks)
qid = {key[1:]: page["pageprops"]["wikibase_item"] for key, page in pages.items() if "wikibase_item" in page.get("pageprops", {})}
values = " ".join(f"wd:{q}" for q in sorted(set(qid.values())))
data = wiki.get("https://query.wikidata.org/sparql", {"format": "json", "query":
    f"SELECT ?item ?at ?height WHERE {{ VALUES ?item {{ {values} }} ?item wdt:P625 ?at . OPTIONAL {{ ?item wdt:P2044 ?height }} }}"})
where, height = {}, {}
for row in data["results"]["bindings"]:
    q = row["item"]["value"].rsplit("/", 1)[1]
    lon, lat = row["at"]["value"][len("Point("):-1].split()
    where.setdefault(q, [round(float(lon), 4), round(float(lat), 4)])
    if "height" in row:
        height[q] = max(height.get(q, 0), round(float(row["height"]["value"])))

cities = []
for name, (de, aliases, tier, state, is_capital, title, f) in content.CITIES.items():
    at = where.get(qid.get(("capital", name)))
    assert at and in_austria(*at), f"no position for {name}: {at}"
    cities.append({"en": name, "de": de, "aliases": aliases, "tier": tier, "state": state, "capital": is_capital, "title": title, "at": at, "facts": facts(f)})
mountains = []
for name, (de, aliases, tier, state, title, f) in content.MOUNTAINS.items():
    q = qid.get(("mountain", name))
    at = where.get(q)
    assert at and in_austria(*at, margin=.06) and height.get(q), f"no position or height for {name}: {at} {height.get(q)}"
    mountains.append({"en": name, "de": de, "aliases": aliases, "tier": tier, "state": state, "title": title, "at": at, "elevation": height[q], "facts": facts(f)})
    print(f"{name}: {height[q]} m at {at}")

data = {"regions": list(content.REGIONS), "states": states, "cities": cities, "mountains": mountains, "rivers": rivers, "lakes": lakes}
OUT.write_text("/* Generated by tools/build_austria.py from tools/austria_content.py. State borders and Lake Constance from Natural Earth "
               "(public domain); other rivers and lakes (c) OpenStreetMap contributors, ODbL; positions and heights from Wikidata (CC0). */\n"
               f"window.BLANK_MAP_AUSTRIA = {json.dumps(data, ensure_ascii=False, separators=(',', ':'))};\n", encoding="utf8")
print("wrote", OUT, OUT.stat().st_size // 1024, "KB")
