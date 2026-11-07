# Mapolo

A browser geography game. Name or find countries, capitals, mountains and rivers on an unlabelled world map, in German or English.

There is also a USA map with the states, their capitals, mountains and rivers, and a Middle-earth map with its lands, places, mountains and rivers.

## Play it

Install [Docker](https://www.docker.com/products/docker-desktop/), start it, then run:

```bash
docker run -d --name blank-map -p 8770:8770 -v blank-map-data:/data ghcr.io/erikfaustmann/blank-map:latest
```

Then open http://localhost:8770. To stop and remove it:

```bash
docker rm -f blank-map
```

Profiles stay in the `blank-map-data` volume when the container is removed.

## Run it from source

With Docker, from this folder:

```bash
docker compose up -d --build
```

Then open http://localhost:8770. To stop it:

```bash
docker compose down
```

Without Docker, run the server with Python 3. It needs no other packages:

```bash
python server.py
```

Then open http://localhost:8770. Profiles are saved in `userdata/blank-map.sqlite`.

The game also runs as plain static files, for example with `python -m http.server`, but without logins or profiles.

## Profiles

You can play without a profile. With one, every answer is saved in a SQLite database. Passwords are stored as scrypt hashes, so nobody can read them, but a profile with an email address can get a reset link.

Accuracy for each category uses the last 30 answers, with each answer counting 7% less than the one after it. Older answers no longer count, so 30 perfect answers in a row always give 100%.

### Password reset by email

Players can add an email address to their profile. If they forget their password, "Forgot your password?" sends them a link that works once, for one hour. For that, the server needs an email account to send from. Put its settings in a file called `.env` next to `compose.yaml`, for example for Gmail with an [app password](https://support.google.com/accounts/answer/185833):

```
BLANK_MAP_SMTP_HOST=smtp.gmail.com
BLANK_MAP_SMTP_PORT=587
BLANK_MAP_SMTP_USER=you@gmail.com
BLANK_MAP_SMTP_PASSWORD=your-app-password
BLANK_MAP_MAIL_FROM=you@gmail.com
BLANK_MAP_PUBLIC_URL=http://localhost:8770
```

`BLANK_MAP_PUBLIC_URL` is where the links in the emails point, so set it to the address players open the game at. For SMTP over SSL on port 465, add `BLANK_MAP_SMTP_SSL=1`. `.env` holds a password, so it stays out of git. Then restart with `docker compose up -d`. Without these settings, the game works as before, just without the "Forgot your password?" link. Running `python server.py` reads the same settings from the environment.

### Managing profiles

To list the profiles, or delete one with all its answers:

```bash
docker compose exec blank-map python server.py --list-profiles
```

```bash
docker compose exec blank-map python server.py --delete-profile "Name"
```

Deleting asks you to type the name again first. Without Docker, run `python server.py --list-profiles` or `python server.py --delete-profile "Name"` instead.

Everyone who runs their own copy has their own separate profiles. To share profiles, host one copy on a server behind HTTPS and set `BLANK_MAP_SECURE_COOKIE=1`. Plain HTTP sends passwords unencrypted, so only use it on your own computer.

## Change the content

Facts about each place live in `facts.js`, which you can edit directly.

Flag codes and the easy and hard lists live in `quiz.js`.

The USA's states, capitals, mountains, rivers and facts live in `tools/usa_content.py`. `tools/build_usa.py` joins them with the map data and writes `usa.js`. It needs these downloads in one folder:

- [states-10m.json](https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/states-10m.json)
- [ne_10m_rivers_north_america.geojson](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_rivers_north_america.geojson)
- ne_10m_rivers_lake_centerlines.geojson and ne_10m_populated_places_simple.geojson, as above

```bash
python tools/build_usa.py path/to/downloads
```

Sights for Earth and the USA live in `tools/sights_content.py`. `tools/build_sights.py` looks up their coordinates on Wikidata and writes `sights.js`. Run `tools/build_images.py` afterwards, so new sights get a photo: a sight's photo is its question, so sights without one are left out.

```bash
python tools/build_sights.py
```

Everything about Middle-earth lives in `middleearth.js`: the coast, lakes and mountain ranges, every place with its facts, and the seed points that decide where each land's borders run. The game builds the map from it when the page loads.

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

US state borders: US Census Bureau, public domain, via [us-atlas](https://github.com/topojson/us-atlas). On the USA map, Alaska and Hawaii are moved into boxes below the mainland and Alaska is shrunk, so distances there are not to scale.

## Pictures

The fact popups show one photo per place from [Wikimedia Commons](https://commons.wikimedia.org/), each under CC0, CC BY, CC BY-SA or in the public domain, with its photographer and license shown underneath. The game stores only each photo's address and credit, so players' browsers load the photos from Wikimedia. To pick them again, run:

```bash
python tools/build_images.py
```

It looks each place up on Wikipedia and Wikidata, caches the answers in `tools/.image-cache/`, and writes `images.js`. Middle-earth gets small drawings instead, made in `index.html`.

## Middle-earth

Middle-earth was created by J.R.R. Tolkien. The map in this game is drawn by hand and only roughly follows his. The facts are written for this game. It is an unofficial fan work, not endorsed by the Tolkien Estate or Middle-earth Enterprises, and the names and setting remain theirs. Check the rights holders' fan policies before publishing it.

## Flags

[flag-icons](https://github.com/lipis/flag-icons), MIT license, included in `flags/`.
