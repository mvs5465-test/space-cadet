from space_cadet.app import IMAGE_CATALOG, app


def test_index_renders_catalog():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Space Cadet" in body
    assert IMAGE_CATALOG[0]["title"] in body
    assert "hero-image" in body
    assert "Open NASA record" in body


def test_healthz():
    client = app.test_client()

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_images_api():
    client = app.test_client()

    response = client.get("/api/images")

    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["images"]) == 3
    assert payload["images"][0]["parts"]
    assert payload["images"][0]["imageUrl"].startswith("/static/images/")
    assert payload["images"][0]["sourceUrl"].startswith("https://images.nasa.gov/details-")
    assert payload["images"][0]["nasaId"]


def test_static_image_asset():
    client = app.test_client()

    response = client.get("/static/images/veil-nebula.svg")

    assert response.status_code == 200
    assert response.mimetype == "image/svg+xml"
