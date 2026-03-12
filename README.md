# space-cadet

Cluster-ready astronomy image browser.

Right now the app is intentionally small: a sidebar of example captures, a main viewer panel, and a details panel for the selected region. It is enough to deploy in-cluster and iterate on the actual image exploration scope later.

## Local run

```bash
pip install -e ".[dev]"
python -m space_cadet.app
```

Then open `http://127.0.0.1:8080`.

## Endpoints

- `GET /` serves the UI
- `GET /api/images` returns the image catalog JSON
- `GET /healthz` returns a simple probe response

## Container

```bash
docker build -t space-cadet .
docker run --rm -p 8080:8080 space-cadet
```

## Helm chart

The repo includes a basic chart in `chart/` using the same simple app-style layout as the other cluster repos.

```bash
helm lint chart
helm template space-cadet chart
```
