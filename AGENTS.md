# AGENTS.md

Instructions for human + AI contributors in this repository.

## Product

- `space-cadet` is a localhost-first astronomy image browser with curated hotspot overlays.
- The current priority is fast local iteration with file-backed NASA data, while still preserving the earlier Docker and Helm deployment path.

## Architecture

- `src/space_cadet/app.py` serves the Flask app and JSON endpoints.
- `src/space_cadet/nasa_import.py` refreshes local NASA-backed assets and metadata.
- `src/space_cadet/data/` holds the generated catalog and curated NASA source list.
- `src/space_cadet/static/images/` stores the local image assets.
- `chart/` and `Dockerfile` are the cluster/deployment layer.

## Working Rules

- Keep the localhost-first workflow fast and deterministic.
- Treat the importer and generated data as part of the product shape, not disposable scaffolding.
- Avoid drifting the cluster artifacts away from the app’s actual runtime needs.
- Update the README when importer behavior or local data layout changes.

## Verification

- Run `pytest` for normal code changes.
- Run `space-cadet-import-nasa` only when intentionally refreshing the local NASA dataset.
- Run the Flask app locally for UI and API changes.
