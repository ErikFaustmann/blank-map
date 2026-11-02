"""Join tools/usa_content.py with US map data and write ../usa.js.

Usage: python -I build_usa.py <dir with the downloads below>

- states-10m.json from us-atlas 3.0.1 (US Census, public domain)
- ne_10m_rivers_north_america.geojson and ne_10m_rivers_lake_centerlines.geojson (Natural Earth, public domain)
- ne_10m_populated_places_simple.geojson (Natural Earth), for the state capitals
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import usa_content as content  # noqa: E402

RAW = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).parent.parent / "usa.js"
SIMPLIFY = 0.02  # degrees, about 2 km


def load(name):
    return json.loads((RAW / name).read_text(encoding="utf8"))


def facts(pairs):
    return [[en for en, _ in pairs], [de for _, de in pairs]]


region_of = {state: region for region, states in content.REGIONS.items() for state in states}

# The states and Washington, D.C. Territories such as Puerto Rico stay out.
topology = load("states-10m.json")
geometries = topology["objects"]["states"]["geometries"]
topology["objects"] = {"states": {**topology["objects"]["states"], "geometries": [g for g in geometries if g["properties"]["name"] in region_of]}}
found = {g["properties"]["name"] for g in topology["objects"]["states"]["geometries"]}
assert found == set(region_of), set(region_of) ^ found

capitals = {}
for f in load("ne_10m_populated_places_simple.geojson")["features"]:
    p = f["properties"]
    if p.get("adm0_a3") == "USA" and p.get("featurecla") == "Admin-1 capital":
        capitals[p["adm1name"]] = [round(p["longitude"], 3), round(p["latitude"], 3)]
assert set(capitals) == set(content.STATES), set(capitals) ^ set(content.STATES)

states = []
for name, (de, aliases, tier, capital, capital_tier, state_facts, capital_facts) in content.STATES.items():
    states.append({"en": name, "de": de, "aliases": aliases, "tier": tier, "region": region_of[name], "facts": facts(state_facts),
                   "capital": {"en": capital, "de": capital, "aliases": ["St. Paul", "St Paul"] if capital == "Saint Paul" else [],
                               "tier": capital_tier, "at": capitals[name], "facts": facts(capital_facts)}})

mountains = []
for name, (de, aliases, tier, (lat, lon), elevation, mountain_facts) in content.MOUNTAINS.items():
    mountains.append({"en": name, "de": de, "aliases": aliases, "tier": tier, "at": [lon, lat], "elevation": elevation, "facts": facts(mountain_facts)})


def lines_of(geometry):
    if geometry["type"] == "LineString":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiLineString":
        return geometry["coordinates"]
    return []


def touches(line, box):
    w, s, e, n = box
    return any(w <= x <= e and s <= y <= n for x, y, *_ in line)


def cut(line, box):
    """Splits a line into the runs of points inside the box."""
    w, s, e, n = box
    runs, run = [], []
    for x, y, *_ in line:
        if w <= x <= e and s <= y <= n:
            run.append([x, y])
        elif run:
            runs.append(run)
            run = []
    return [r for r in runs + [run] if len(r) > 1]


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


features = load("ne_10m_rivers_north_america.geojson")["features"] + load("ne_10m_rivers_lake_centerlines.geojson")["features"]
rivers = []
for name, (de, aliases, tier, region, ne_names, box, clip, river_facts) in content.RIVERS.items():
    wanted = {n.lower() for n in ne_names}
    lines, seen = [], set()
    for f in features:
        p = f["properties"]
        if (p.get("name") or "").lower() not in wanted and (p.get("name_en") or "").lower() not in wanted:
            continue
        for line in lines_of(f["geometry"]):
            key = tuple(tuple(round(c, 3) for c in pt[:2]) for pt in line)
            if key in seen or not touches(line, box):
                continue
            seen.add(key)
            for run in cut(line, clip) if clip else [[pt[:2] for pt in line]]:
                lines.append([[round(x, 3), round(y, 3)] for x, y in simplify(run, SIMPLIFY)])
    assert lines, name
    rivers.append({"en": name, "de": de, "aliases": aliases, "tier": tier, "region": region, "lines": lines, "facts": facts(river_facts)})
    print(f"{name}: {len(lines)} lines, {sum(len(l) for l in lines)} points")

data = {"regions": list(content.REGIONS), "topology": topology, "states": states, "mountains": mountains, "rivers": rivers}
OUT.write_text("/* Generated by tools/build_usa.py from tools/usa_content.py. US Census state borders via us-atlas, "
               "rivers and capitals from Natural Earth, all public domain. */\n"
               f"window.BLANK_MAP_USA = {json.dumps(data, ensure_ascii=False, separators=(',', ':'))};\n", encoding="utf8")
print("wrote", OUT, OUT.stat().st_size // 1024, "KB")
