"""Space Cadet web application."""

from __future__ import annotations

import json
import os

from flask import Flask, jsonify


IMAGE_CATALOG = [
    {
        "id": "veil-nebula",
        "title": "Veil Nebula",
        "subtitle": "Supernova remnant sweep",
        "summary": "Trace the shock-front filaments and compare bright knots across the frame.",
        "background": "linear-gradient(135deg, #020617 0%, #102a43 45%, #0f766e 100%)",
        "parts": [
            {
                "id": "western-arc",
                "name": "Western Arc",
                "focus": "High-contrast filament band with bright cyan edges.",
                "details": "Useful for comparing narrow gas ribbons against the darker field.",
            },
            {
                "id": "core-knots",
                "name": "Core Knots",
                "focus": "Dense pocket of overlapping structures near the image center.",
                "details": "Good candidate for overlays and quick annotation prototypes.",
            },
            {
                "id": "outer-field",
                "name": "Outer Field",
                "focus": "Dimmer stars and ambient glow at the edge of the capture.",
                "details": "Helps validate contrast controls without obscuring the target.",
            },
        ],
    },
    {
        "id": "eagle-nebula",
        "title": "Eagle Nebula",
        "subtitle": "Pillars and dust structures",
        "summary": "Browse dusty columns and brighter ridges to test simple guided exploration.",
        "background": "linear-gradient(135deg, #140f2d 0%, #4c1d95 40%, #f97316 100%)",
        "parts": [
            {
                "id": "pillar-band",
                "name": "Pillar Band",
                "focus": "Tall dust structures with warm highlights and sharp boundaries.",
                "details": "Useful for zoom states and side-by-side region descriptions.",
            },
            {
                "id": "ridge-line",
                "name": "Ridge Line",
                "focus": "Bright ionized edge where the scene shifts from dust to glow.",
                "details": "Good for testing labels that need to stay readable on bright areas.",
            },
            {
                "id": "star-field",
                "name": "Star Field",
                "focus": "Sparse but bright stars scattered around the pillars.",
                "details": "Acts as a clean fallback view when no feature is selected.",
            },
        ],
    },
    {
        "id": "andromeda",
        "title": "Andromeda Galaxy",
        "subtitle": "Wide-frame spiral structure",
        "summary": "Use the menu to jump between core glow, dust lanes, and the outer halo.",
        "background": "linear-gradient(135deg, #0f172a 0%, #1d4ed8 45%, #f8fafc 100%)",
        "parts": [
            {
                "id": "core-glow",
                "name": "Core Glow",
                "focus": "Bright central region with soft radial fade.",
                "details": "Best for validating intensity scaling and summary cards.",
            },
            {
                "id": "dust-lanes",
                "name": "Dust Lanes",
                "focus": "Thin diagonal bands that break up the brighter spiral disk.",
                "details": "Ideal for future polygon overlays or feature extraction markers.",
            },
            {
                "id": "outer-halo",
                "name": "Outer Halo",
                "focus": "Low-signal edges where the galaxy fades into the background.",
                "details": "A simple place to test background subtraction ideas later.",
            },
        ],
    },
]

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
      grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.8fr);
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
      min-height: 480px;
      padding: 28px;
    }
    .canvas::before,
    .canvas::after {
      content: "";
      position: absolute;
      border-radius: 999px;
      filter: blur(6px);
      opacity: 0.75;
    }
    .canvas::before {
      inset: 10% auto auto 12%;
      width: 42%;
      height: 42%;
      background: radial-gradient(circle, rgba(255, 255, 255, 0.8), transparent 72%);
    }
    .canvas::after {
      inset: auto 12% 14% auto;
      width: 28%;
      height: 28%;
      background: radial-gradient(circle, rgba(125, 211, 252, 0.6), transparent 70%);
    }
    .canvas-grid {
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
      background-size: 56px 56px;
      mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.7), transparent);
    }
    .canvas-copy {
      position: relative;
      max-width: 360px;
      z-index: 1;
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
      background: rgba(2, 6, 23, 0.44);
      border: 1px solid rgba(255, 255, 255, 0.12);
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
      .canvas {
        min-height: 360px;
      }
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
            <div class="canvas-grid"></div>
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
          </div>
        </section>
        <aside class="panel details">
          <p class="subtitle">Current target</p>
          <h2 id="details-title"></h2>
          <p id="details-summary"></p>
          <div class="part-list" id="part-list"></div>
          <div class="cluster-note">
            Deployed in-cluster, this can stay simple:
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
      activeImage.parts.forEach((part) => {
        const button = document.createElement("button");
        button.className = part.id === activePart.id ? "active" : "";
        button.innerHTML = `<strong>${part.name}</strong><span>${part.focus}</span>`;
        button.addEventListener("click", () => {
          activePart = part;
          render();
        });
        partList.appendChild(button);
      });
    }

    function renderDetails() {
      canvas.style.background = activeImage.background;
      document.getElementById("hero-subtitle").textContent = activeImage.subtitle;
      document.getElementById("hero-title").textContent = activeImage.title;
      document.getElementById("hero-summary").textContent = activeImage.summary;
      document.getElementById("focus-name").textContent = activePart.name;
      document.getElementById("focus-text").textContent = activePart.details;
      document.getElementById("details-title").textContent = activeImage.title;
      document.getElementById("details-summary").textContent = activeImage.summary;
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
    app = Flask(__name__)

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
