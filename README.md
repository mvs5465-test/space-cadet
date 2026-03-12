# space-cadet

Astronomy image browser for fast local iteration.

Right now the app is intentionally small: a sidebar of captures, an actual in-repo image viewer, and named hotspot regions with detail cards. The point of this pass is to iterate locally on the app shape before worrying about cluster integration again.

The image data now comes from NASA's Image and Video Library, but it is still pulled into local files so the app stays fast and deterministic while you iterate.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m space_cadet.app
```

Then open `http://127.0.0.1:8080`.

## Current local data model

- image metadata lives in `src/space_cadet/data/images.json`
- curated NASA source IDs live in `src/space_cadet/data/nasa_sources.json`
- local image assets live in `src/space_cadet/static/images/`
- each region currently uses a single hotspot with percentage coordinates

That gives us a simple next step for real images later: keep the NASA importer, swap hotspot points for boxes or polygons, and add richer per-region notes.

## Refresh NASA data

```bash
source .venv/bin/activate
space-cadet-import-nasa
```

That command:

- fetches the curated NASA records listed in `nasa_sources.json`
- downloads local image files into `src/space_cadet/static/images/nasa/`
- regenerates `src/space_cadet/data/images.json`

## Endpoints

- `GET /` serves the UI
- `GET /api/images` returns the image catalog JSON
- `GET /healthz` returns a simple probe response

## Notes

- The repo still keeps the Dockerfile and chart from the earlier cluster-ready pass.
- For now the fastest loop is the local Flask app with repo-backed NASA assets and generated JSON data.
