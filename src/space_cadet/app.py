"""Space Cadet web application."""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, jsonify


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "images.json"


def load_catalog() -> list[dict[str, object]]:
    """Load the local image catalog used by the app."""
    payload = json.loads(DATA_PATH.read_text())
    images = payload["images"]
    for image in images:
        image["imageUrl"] = f"/static/{image['asset']}"
    return images


IMAGE_CATALOG = load_catalog()

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Space Cadet</title>
  <style>
    :root {
      --bg: #030712;
      --panel: rgba(10, 15, 30, 0.88);
      --panel-strong: rgba(15, 23, 42, 0.95);
      --ink: #e5eefb;
      --muted: #93a4bf;
      --line: rgba(148, 163, 184, 0.18);
      --accent: #7dd3fc;
      --accent-ink: #06223a;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top right, rgba(125, 211, 252, 0.18), transparent 22%),
        radial-gradient(circle at bottom left, rgba(249, 115, 22, 0.16), transparent 28%),
        linear-gradient(180deg, #020617 0%, var(--bg) 100%);
      min-height: 100vh;
    }
    .shell {
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
      min-height: 100vh;
    }
    .sidebar {
      border-right: 1px solid var(--line);
      background: rgba(2, 6, 23, 0.78);
      padding: 28px 20px;
      backdrop-filter: blur(18px);
    }
    .brand {
      margin-bottom: 24px;
    }
    .eyebrow {
      display: inline-block;
      margin-bottom: 10px;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 0.74rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      background: rgba(125, 211, 252, 0.14);
      color: var(--accent);
    }
    h1 {
      margin: 0;
      font-size: 2.3rem;
      line-height: 0.95;
      letter-spacing: -0.04em;
    }
    .tagline {
      margin: 12px 0 0;
      color: var(--muted);
      line-height: 1.5;
    }
    .menu-label {
      margin: 28px 0 10px;
      color: var(--muted);
      font-size: 0.8rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .menu {
      display: grid;
      gap: 10px;
    }
    .menu button {
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px;
      text-align: left;
      color: var(--ink);
      background: rgba(15, 23, 42, 0.66);
      cursor: pointer;
    }
    .menu button.active {
      border-color: rgba(125, 211, 252, 0.7);
      background: rgba(14, 116, 144, 0.22);
    }
    .menu strong,
    .part-list strong {
      display: block;
      margin-bottom: 4px;
      font-size: 0.98rem;
    }
    .menu span,
    .part-list span {
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.4;
    }
    .content {
      padding: 32px;
    }
    .hero {
      display: grid;
      gap: 22px;
      grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.8fr);
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--panel);
      box-shadow: 0 24px 80px rgba(2, 6, 23, 0.42);
      overflow: hidden;
    }
    .canvas {
      position: relative;
      min-height: 540px;
      background: linear-gradient(180deg, rgba(2, 6, 23, 0.5), rgba(2, 6, 23, 0.1));
    }
    .canvas-copy {
      position: relative;
      max-width: 360px;
      z-index: 1;
      padding: 28px 28px 0;
    }
    .canvas-copy h2 {
      margin: 12px 0 6px;
      font-size: clamp(2rem, 5vw, 4.4rem);
      line-height: 0.92;
      letter-spacing: -0.05em;
    }
    .canvas-copy p {
      margin: 0;
      color: rgba(226, 232, 240, 0.92);
      line-height: 1.6;
    }
    .focus-card {
      margin-top: 22px;
      padding: 16px 18px;
      border-radius: 18px;
      background: rgba(2, 6, 23, 0.52);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .viewer {
      position: relative;
      margin: 22px 28px 28px;
      aspect-ratio: 4 / 3;
      border-radius: 22px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.12);
      background: rgba(2, 6, 23, 0.45);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.04);
    }
    .viewer img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .overlay {
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.06) 1px, transparent 1px);
      background-size: 56px 56px;
      pointer-events: none;
    }
    .hotspot {
      position: absolute;
      transform: translate(-50%, -50%);
      width: 22px;
      height: 22px;
      border-radius: 999px;
      border: 2px solid rgba(255, 255, 255, 0.95);
      background: rgba(125, 211, 252, 0.4);
      box-shadow: 0 0 0 10px rgba(125, 211, 252, 0.12);
      cursor: pointer;
    }
    .hotspot.active {
      background: rgba(249, 115, 22, 0.8);
      box-shadow: 0 0 0 14px rgba(249, 115, 22, 0.18);
    }
    .hotspot-label {
      position: absolute;
      left: 50%;
      top: calc(100% + 10px);
      transform: translateX(-50%);
      white-space: nowrap;
      padding: 6px 9px;
      border-radius: 999px;
      background: rgba(2, 6, 23, 0.82);
      color: var(--ink);
      font-size: 0.78rem;
      font-weight: 600;
    }
    .focus-card h3,
    .details h3 {
      margin: 0 0 10px;
      font-size: 0.86rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .details {
      padding: 22px;
      background: var(--panel-strong);
    }
    .details .subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 0.94rem;
    }
    .details h2 {
      margin: 10px 0;
      font-size: 1.8rem;
    }
    .part-list {
      display: grid;
      gap: 12px;
      margin-top: 18px;
    }
    .part-list button {
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px;
      background: rgba(2, 6, 23, 0.35);
      text-align: left;
      color: var(--ink);
      cursor: pointer;
    }
    .part-list button.active {
      border-color: rgba(249, 115, 22, 0.72);
      background: rgba(194, 65, 12, 0.16);
    }
    .cluster-note {
      margin-top: 18px;
      padding: 16px 18px;
      border-radius: 18px;
      background: rgba(125, 211, 252, 0.08);
      border: 1px solid rgba(125, 211, 252, 0.16);
      color: var(--muted);
      line-height: 1.5;
    }
    .meta-grid {
      display: grid;
      gap: 10px;
      margin-top: 18px;
    }
    .meta-item {
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(2, 6, 23, 0.28);
    }
    .meta-item strong {
      display: block;
      margin-bottom: 6px;
      font-size: 0.76rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }
    .meta-item a {
      color: var(--accent);
      text-decoration: none;
    }
    .meta-item a:hover {
      text-decoration: underline;
    }
    code {
      font-family: "SF Mono", "Menlo", monospace;
      color: var(--accent);
    }
    @media (max-width: 920px) {
      .shell {
        grid-template-columns: 1fr;
      }
      .sidebar {
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }
      .hero {
        grid-template-columns: 1fr;
      }
      .content {
        padding: 22px;
      }
      .canvas { min-height: 0; }
      .viewer { margin: 22px; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="eyebrow">Cluster-ready viewer</div>
        <h1>Space Cadet</h1>
        <p class="tagline">A simple image browser for astronomy captures with room for region-by-region exploration later.</p>
      </div>
      <div class="menu-label">Image library</div>
      <div class="menu" id="image-menu"></div>
    </aside>
    <section class="content">
      <div class="hero">
        <section class="panel">
          <div class="canvas" id="canvas">
            <div class="canvas-copy">
              <div class="eyebrow" id="hero-subtitle"></div>
              <h2 id="hero-title"></h2>
              <p id="hero-summary"></p>
              <div class="focus-card">
                <h3>Selected Region</h3>
                <strong id="focus-name"></strong>
                <p id="focus-text"></p>
              </div>
            </div>
            <div class="viewer">
              <img id="hero-image" alt="">
              <div class="overlay"></div>
              <div id="hotspot-layer"></div>
            </div>
          </div>
        </section>
        <aside class="panel details">
          <p class="subtitle">Current target</p>
          <h2 id="details-title"></h2>
          <p id="details-summary"></p>
          <div class="meta-grid">
            <div class="meta-item">
              <strong>NASA ID</strong>
              <span id="details-nasa-id"></span>
            </div>
            <div class="meta-item">
              <strong>Date Created</strong>
              <span id="details-date"></span>
            </div>
            <div class="meta-item">
              <strong>Credit</strong>
              <span id="details-credit"></span>
            </div>
            <div class="meta-item">
              <strong>Source</strong>
              <a id="details-source" href="" target="_blank" rel="noreferrer">Open NASA record</a>
            </div>
          </div>
          <div class="part-list" id="part-list"></div>
          <div class="cluster-note">
            For local iteration this stays dead simple:
            <code>/</code> for the UI,
            <code>/api/images</code> for data,
            and <code>/healthz</code> for probes.
          </div>
        </aside>
      </div>
    </section>
  </main>
  <script>
    const catalog = __CATALOG__;
    let activeImage = catalog[0];
    let activePart = activeImage.parts[0];

    const imageMenu = document.getElementById("image-menu");
    const partList = document.getElementById("part-list");
    const canvas = document.getElementById("canvas");
    const hotspotLayer = document.getElementById("hotspot-layer");
    const heroImage = document.getElementById("hero-image");

    function renderImageMenu() {
      imageMenu.innerHTML = "";
      catalog.forEach((image) => {
        const button = document.createElement("button");
        button.className = image.id === activeImage.id ? "active" : "";
        button.innerHTML = `<strong>${image.title}</strong><span>${image.subtitle}</span>`;
        button.addEventListener("click", () => {
          activeImage = image;
          activePart = image.parts[0];
          render();
        });
        imageMenu.appendChild(button);
      });
    }

    function renderParts() {
      partList.innerHTML = "";
      hotspotLayer.innerHTML = "";
      activeImage.parts.forEach((part) => {
        const button = document.createElement("button");
        button.className = part.id === activePart.id ? "active" : "";
        button.innerHTML = `<strong>${part.name}</strong><span>${part.focus}</span>`;
        button.addEventListener("click", () => {
          activePart = part;
          render();
        });
        partList.appendChild(button);

        const hotspot = document.createElement("button");
        hotspot.className = part.id === activePart.id ? "hotspot active" : "hotspot";
        hotspot.style.left = `${part.hotspot.x}%`;
        hotspot.style.top = `${part.hotspot.y}%`;
        hotspot.setAttribute("aria-label", part.name);
        hotspot.innerHTML = `<span class="hotspot-label">${part.name}</span>`;
        hotspot.addEventListener("click", () => {
          activePart = part;
          render();
        });
        hotspotLayer.appendChild(hotspot);
      });
    }

    function renderDetails() {
      canvas.style.background = activeImage.background;
      heroImage.src = activeImage.imageUrl;
      heroImage.alt = activeImage.title;
      document.getElementById("hero-subtitle").textContent = activeImage.subtitle;
      document.getElementById("hero-title").textContent = activeImage.title;
      document.getElementById("hero-summary").textContent = activeImage.summary;
      document.getElementById("focus-name").textContent = activePart.name;
      document.getElementById("focus-text").textContent = activePart.details;
      document.getElementById("details-title").textContent = activeImage.title;
      document.getElementById("details-summary").textContent = activeImage.summary;
      document.getElementById("details-nasa-id").textContent = activeImage.nasaId;
      document.getElementById("details-date").textContent = activeImage.dateCreated;
      document.getElementById("details-credit").textContent = activeImage.credit;
      const source = document.getElementById("details-source");
      source.href = activeImage.sourceUrl;
    }

    function render() {
      renderImageMenu();
      renderParts();
      renderDetails();
    }

    render();
  </script>
</body>
</html>
"""


def create_app() -> Flask:
    """Create the Flask application."""
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    @app.get("/")
    def index() -> str:
        return INDEX_HTML.replace("__CATALOG__", json.dumps(IMAGE_CATALOG))

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    @app.get("/api/images")
    def images():
        return jsonify({"images": IMAGE_CATALOG})

    return app


app = create_app()


def main() -> None:
    """Run the development server."""
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
