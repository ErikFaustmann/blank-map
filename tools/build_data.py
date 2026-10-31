"""Join tools/content.py with Natural Earth geometry and write ../data.js.

Usage: python -I build_data.py <dir with countries-50m.json and ne_* geojson files>
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import content  # noqa: E402
import content_de as de  # noqa: E402

RAW = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(__file__).parent.parent / "data.js"


def load(name):
    return json.loads((RAW / name).read_text(encoding="utf8"))


def norm(text):
    text = unicodedata.normalize("NFD", str(text or ""))
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = re.sub(r"\s+", " ", text.replace("’", "'")).strip()
    return text


def split(text):
    return [part.strip() for part in text.split(";") if part.strip()]


def german(table, key):
    """German (name, aliases) for an English name, which is also the fallback."""
    parts = split(table.get(key, key))
    return parts[0], parts[1:]


def german_block(table, key, **extra):
    name, aliases = german(table, key)
    return {"name": name, "aliases": aliases, **extra}


def german_where(where):
    def one(place):
        return de.WHERE.get(place) or german(de.COUNTRIES, place)[0]
    return " und ".join(one(p) for p in where.split(" and "))


world = load("countries-50m.json")
atlas_names = {g["properties"]["name"] for g in world["objects"]["countries"]["geometries"]}
atlas_by_norm = {norm(n): n for n in atlas_names}

# Capital coordinates: prefer the row flagged as a country capital.
places = {}
for feature in load("ne_10m_populated_places_simple.geojson")["features"]:
    p = feature["properties"]
    for key in {norm(p.get("name")), norm(p.get("nameascii"))}:
        known = places.get(key)
        rank = (p.get("adm0cap") or 0, p.get("pop_max") or 0)
        if not known or rank > known[0]:
            places[key] = (rank, (round(p["longitude"], 3), round(p["latitude"], 3)), p.get("adm0name"))

problems = []
countries = []
for region, block in content.COUNTRIES.items():
    for line in block.strip().splitlines():
        name, atlas, capital, aliases, capital_aliases = line.split("|")
        atlas_name = atlas_by_norm.get(norm(atlas or name))
        if not atlas_name and name not in content.ADD_POINT_COUNTRIES:
            problems.append(f"no shape: {name}")
        coords = None
        if capital:
            coords = content.CAPITAL_COORDS.get(capital)
            if not coords:
                found = places.get(norm(capital))
                if found:
                    coords = found[1]
                else:
                    problems.append(f"no capital coords: {capital} ({name})")
        countries.append({
            "name": name,
            "shape": atlas_name,
            "extra": content.MERGE_INTO.get(name, []),
            "point": content.ADD_POINT_COUNTRIES.get(name),
            "region": region,
            "aliases": split(aliases),
            "capital": capital or None,
            "capitalAliases": split(capital_aliases),
            "capitalCoord": coords,
            "capitalNote": content.CAPITAL_NOTES.get(capital),
            "de": german_block(de.COUNTRIES, name),
            "capitalDe": german_block(de.CAPITALS, capital, note=de.CAPITAL_NOTES.get(capital)) if capital else None,
        })

mountains = [
    {"name": n, "coord": [lon, lat], "elevation": e, "range": rng, "where": where,
     "aliases": split(al), "region": region,
     "de": german_block(de.MOUNTAINS, n, range=de.RANGES.get(rng, rng), where=german_where(where))}
    for n, lat, lon, e, rng, where, al, region in content.MOUNTAINS
]


def segments(features, names, bbox):
    wanted = {norm(n) for n in split(names)}
    lines = []
    for feature in features:
        if norm(feature["properties"].get("name")) not in wanted or not feature["geometry"]:
            continue
        geom = feature["geometry"]
        parts = geom["coordinates"] if geom["type"] == "MultiLineString" else [geom["coordinates"]]
        for part in parts:
            if bbox and not all(bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3] for x, y, *_ in part):
                continue
            lines.append([[round(x, 2), round(y, 2)] for x, y, *_ in part])
    return lines


river_features = load("ne_50m_rivers_lake_centerlines.geojson")["features"]
detailed_features = load("ne_10m_rivers_lake_centerlines.geojson")["features"]
rivers = []
for name, parts, length, mouth, aliases, region, bbox in content.RIVERS:
    lines = content.RIVER_LINES.get(name) or segments(river_features, parts, bbox) or segments(detailed_features, parts, bbox)
    if not lines:
        problems.append(f"no river: {name}")
        continue
    rivers.append({"name": name, "lines": lines, "length": length, "mouth": mouth,
                   "aliases": split(aliases), "region": region,
                   "de": german_block(de.RIVERS, name, mouth=de.MOUTHS.get(mouth))})
    if mouth not in de.MOUTHS:
        problems.append(f"no German mouth: {mouth}")

# A German key that matches nothing is a typo and would silently fall back to English.
english = {
    "COUNTRIES": {c["name"] for c in countries},
    "CAPITALS": {c["capital"] for c in countries},
    "CAPITAL_NOTES": {c["capital"] for c in countries},
    "MOUNTAINS": {m[0] for m in content.MOUNTAINS},
    "RANGES": {m[4] for m in content.MOUNTAINS},
    "RIVERS": {r[0] for r in content.RIVERS},
    "MOUTHS": {r[3] for r in content.RIVERS},
}
for table, known in english.items():
    problems += [f"unknown German key in {table}: {k}" for k in getattr(de, table) if k not in known]

data = {"world": world, "countries": countries, "mountains": mountains, "rivers": rivers}
OUT.write_text("window.BLANK_MAP_DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";",
               encoding="utf8")
print(f"{len(countries)} countries, {len(mountains)} mountains, {len(rivers)} rivers; "
      f"{OUT.stat().st_size // 1024} KB")
print("Problems:", problems or "none")
for c in countries:
    if c["capital"] and c["capital"] not in content.CAPITAL_COORDS:
        adm = places.get(norm(c["capital"]))
        if adm and adm[0][0] != 1:
            print("not flagged as a capital:", c["capital"], "->", adm[2], adm[1])
