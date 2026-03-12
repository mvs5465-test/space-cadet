"""NASA Image and Video Library importer for local app data."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen


PACKAGE_DIR = Path(__file__).resolve().parent
SEED_PATH = PACKAGE_DIR / "data" / "nasa_sources.json"
OUTPUT_PATH = PACKAGE_DIR / "data" / "images.json"
STATIC_IMAGE_DIR = PACKAGE_DIR / "static" / "images" / "nasa"
NASA_SEARCH_URL = "https://images-api.nasa.gov/search"


def fetch_json(url: str) -> dict[str, object]:
    """Fetch JSON from a URL."""
    with urlopen(url) as response:
        return json.load(response)


def fetch_binary(url: str) -> bytes:
    """Fetch binary content from a URL."""
    with urlopen(url) as response:
        return response.read()


def slugify(value: str) -> str:
    """Convert a string into a filename-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def first_sentence(text: str) -> str:
    """Return the first sentence-like chunk of text."""
    collapsed = " ".join(text.split())
    match = re.match(r"(.+?[.!?])(?:\s|$)", collapsed)
    return match.group(1) if match else collapsed


def build_source_url(nasa_id: str) -> str:
    """Build the public NASA record URL for an image."""
    return f"https://images.nasa.gov/details-{nasa_id}"


def pick_image_link(links: list[dict[str, object]]) -> str:
    """Pick a preferred downloadable image URL."""
    preferred_suffixes = ("~medium.jpg", "~large.jpg", "~orig.jpg", ".jpg", ".png")
    hrefs = [link["href"] for link in links if link.get("render") == "image"]
    for suffix in preferred_suffixes:
        for href in hrefs:
            if href.endswith(suffix):
                return href
    if not hrefs:
        raise ValueError("No downloadable image links found in NASA response")
    return hrefs[0]


def extension_for_url(url: str) -> str:
    """Determine a local file extension from a remote URL."""
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return suffix
    guessed, _ = mimetypes.guess_type(path)
    if guessed:
        return mimetypes.guess_extension(guessed) or ".jpg"
    return ".jpg"


def fetch_nasa_record(
    nasa_id: str,
    fetch_json_fn=fetch_json,
) -> dict[str, object]:
    """Fetch one NASA record by ID."""
    url = f"{NASA_SEARCH_URL}?{urlencode({'nasa_id': nasa_id, 'media_type': 'image'})}"
    payload = fetch_json_fn(url)
    items = payload["collection"]["items"]
    if not items:
        raise ValueError(f"No NASA image found for {nasa_id}")
    item = items[0]
    metadata = item["data"][0]
    image_url = pick_image_link(item.get("links", []))
    return {
        "nasaId": nasa_id,
        "title": metadata["title"],
        "description": metadata.get("description_508") or metadata.get("description") or "",
        "dateCreated": metadata.get("date_created", "")[:10],
        "credit": metadata.get("secondary_creator") or metadata.get("center") or "NASA",
        "sourceUrl": build_source_url(nasa_id),
        "imageUrl": image_url,
    }


def build_catalog(
    seed_items: list[dict[str, object]],
    fetch_json_fn=fetch_json,
    fetch_binary_fn=fetch_binary,
    static_image_dir: Path = STATIC_IMAGE_DIR,
) -> list[dict[str, object]]:
    """Build a local app catalog from curated NASA source items."""
    static_image_dir.mkdir(parents=True, exist_ok=True)
    catalog: list[dict[str, object]] = []

    for seed in seed_items:
        record = fetch_nasa_record(seed["nasaId"], fetch_json_fn=fetch_json_fn)
        extension = extension_for_url(record["imageUrl"])
        asset_name = f"{seed['id']}{extension}"
        asset_path = static_image_dir / asset_name
        asset_path.write_bytes(fetch_binary_fn(record["imageUrl"]))
        summary = first_sentence(record["description"]) or record["title"]

        catalog.append(
            {
                "id": seed["id"],
                "nasaId": record["nasaId"],
                "title": record["title"],
                "subtitle": seed["subtitle"],
                "summary": summary,
                "description": record["description"],
                "credit": record["credit"],
                "dateCreated": record["dateCreated"],
                "sourceUrl": record["sourceUrl"],
                "background": seed["background"],
                "asset": f"images/nasa/{asset_name}",
                "parts": seed["parts"],
            }
        )

    return catalog


def refresh_catalog(
    seed_path: Path = SEED_PATH,
    output_path: Path = OUTPUT_PATH,
    static_image_dir: Path = STATIC_IMAGE_DIR,
    fetch_json_fn=fetch_json,
    fetch_binary_fn=fetch_binary,
) -> list[dict[str, object]]:
    """Refresh the app catalog and local image assets from NASA."""
    seed_payload = json.loads(seed_path.read_text())
    catalog = build_catalog(
        seed_payload["images"],
        fetch_json_fn=fetch_json_fn,
        fetch_binary_fn=fetch_binary_fn,
        static_image_dir=static_image_dir,
    )
    output_path.write_text(json.dumps({"images": catalog}, indent=2) + "\n")
    return catalog


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Refresh local Space Cadet data from NASA.")
    parser.add_argument(
        "--seed-path",
        default=str(SEED_PATH),
        help="Path to the curated NASA source config.",
    )
    parser.add_argument(
        "--output-path",
        default=str(OUTPUT_PATH),
        help="Path to the generated images.json catalog.",
    )
    parser.add_argument(
        "--static-image-dir",
        default=str(STATIC_IMAGE_DIR),
        help="Directory for downloaded NASA image assets.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    catalog = refresh_catalog(
        seed_path=Path(args.seed_path),
        output_path=Path(args.output_path),
        static_image_dir=Path(args.static_image_dir),
    )
    print(f"refreshed {len(catalog)} NASA images into {args.output_path}")


if __name__ == "__main__":
    main()
