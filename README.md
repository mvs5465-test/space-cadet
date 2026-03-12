# space-cadet

Astronomy image browser for fast local iteration.

Right now the app is intentionally small: a sidebar of captures, an actual in-repo image viewer, and named hotspot regions with detail cards. The point of this pass is to iterate locally on the app shape before worrying about cluster integration again.

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
- local image assets live in `src/space_cadet/static/images/`
- each region currently uses a single hotspot with percentage coordinates

That gives us a simple next step for real images later: swap the SVG assets for actual captures and evolve the hotspot model into boxes or polygons.

## Endpoints

- `GET /` serves the UI
- `GET /api/images` returns the image catalog JSON
- `GET /healthz` returns a simple probe response

## Notes

- The repo still keeps the Dockerfile and chart from the earlier cluster-ready pass.
- For now the fastest loop is the local Flask app with repo-backed assets and JSON data.
