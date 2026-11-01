# Blank Map

A browser geography game. Name or find countries, capitals, mountains and rivers on an unlabelled world map, in German or English.

## Play it

Install [Docker](https://www.docker.com/products/docker-desktop/), start it, then run:

```bash
docker run -d --name blank-map -p 8770:80 ghcr.io/erikfaustmann/blank-map:latest
```

Then open http://localhost:8770. To stop and remove it:

```bash
docker rm -f blank-map
```

## Run it from source

With Docker, from this folder:

```bash
docker compose up -d --build
```

Then open http://localhost:8770. To stop it:

```bash
docker compose down
```

Without Docker, serve the folder with Python. The page loads `data.js`, so opening the file directly won't work:

```bash
python -m http.server 8770 --directory .
```

## Change the content

Facts about each place live in `facts.js`, which you can edit directly.

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
