import json
from pathlib import Path

from space_cadet.nasa_import import build_catalog, refresh_catalog


def test_build_catalog_downloads_seeded_images(tmp_path: Path):
    seed_items = [
        {
            "id": "demo-image",
            "nasaId": "PIA00001",
            "subtitle": "Demo subtitle",
            "background": "linear-gradient(180deg, #000, #111)",
            "parts": [
                {
                    "id": "demo-region",
                    "name": "Demo Region",
                    "focus": "Focus text",
                    "details": "Detail text",
                    "hotspot": {"x": 50, "y": 50},
                }
            ],
        }
    ]

    def fake_fetch_json(url: str):
        assert "PIA00001" in url
        return {
            "collection": {
                "items": [
                    {
                        "data": [
                            {
                                "title": "Demo NASA Image",
                                "description": "First sentence. Second sentence.",
                                "date_created": "2026-03-12T00:00:00Z",
                                "secondary_creator": "NASA/Test Center",
                            }
                        ],
                        "links": [
                            {
                                "href": "https://example.test/demo~medium.jpg",
                                "render": "image",
                            }
                        ],
                    }
                ]
            }
        }

    def fake_fetch_binary(url: str):
        assert url.endswith(".jpg")
        return b"jpeg-bytes"

    catalog = build_catalog(
        seed_items,
        fetch_json_fn=fake_fetch_json,
        fetch_binary_fn=fake_fetch_binary,
        static_image_dir=tmp_path / "images",
    )

    assert catalog[0]["title"] == "Demo NASA Image"
    assert catalog[0]["summary"] == "First sentence."
    assert catalog[0]["asset"] == "images/nasa/demo-image.jpg"
    assert catalog[0]["credit"] == "NASA/Test Center"
    assert (tmp_path / "images" / "demo-image.jpg").read_bytes() == b"jpeg-bytes"


def test_refresh_catalog_writes_output_file(tmp_path: Path):
    seed_path = tmp_path / "nasa_sources.json"
    output_path = tmp_path / "images.json"
    static_image_dir = tmp_path / "static"

    seed_path.write_text(
        json.dumps(
            {
                "images": [
                    {
                        "id": "demo-image",
                        "nasaId": "PIA00001",
                        "subtitle": "Demo subtitle",
                        "background": "linear-gradient(180deg, #000, #111)",
                        "parts": [],
                    }
                ]
            }
        )
    )

    def fake_fetch_json(url: str):
        return {
            "collection": {
                "items": [
                    {
                        "data": [
                            {
                                "title": "Demo NASA Image",
                                "description_508": "Accessible description.",
                                "date_created": "2026-03-12T00:00:00Z",
                                "center": "NASA",
                            }
                        ],
                        "links": [
                            {
                                "href": "https://example.test/demo~large.jpg",
                                "render": "image",
                            }
                        ],
                    }
                ]
            }
        }

    def fake_fetch_binary(_url: str):
        return b"bytes"

    refresh_catalog(
        seed_path=seed_path,
        output_path=output_path,
        static_image_dir=static_image_dir,
        fetch_json_fn=fake_fetch_json,
        fetch_binary_fn=fake_fetch_binary,
    )

    payload = json.loads(output_path.read_text())
    assert payload["images"][0]["dateCreated"] == "2026-03-12"
    assert payload["images"][0]["sourceUrl"].endswith("PIA00001")
    assert (static_image_dir / "demo-image.jpg").exists()
