# Blank Map

A browser geography game. Name or find countries, capitals, mountains and rivers on an unlabelled world map, in German or English.

## Run it

The page loads `data.js`, so serve the folder instead of opening the file directly:

```bash
python -m http.server 8770 --directory .
```

Then open http://localhost:8770.

## Change the content

Places live in `tools/content.py`, with German names in `tools/content_de.py`. `tools/build_data.py` joins them with the map data and writes `data.js`.

Download these into an empty folder, then pass that folder to the script:

- [countries-50m.json](https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json)
- [ne_50m_rivers_lake_centerlines.geojson](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_rivers_lake_centerlines.geojson)
- [ne_10m_rivers_lake_centerlines.geojson](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_rivers_lake_centerlines.geojson)
- [ne_10m_populated_places_simple.geojson](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_populated_places_simple.geojson)

```bash
python tools/build_data.py path/to/downloads
```

## Map data

[Natural Earth](https://www.naturalearthdata.com/), public domain, via [world-atlas](https://github.com/topojson/world-atlas).
