from src.features.web import create_app


def test_index():
    app = create_app()
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200


def test_api_metrics():
    app = create_app()
    client = app.test_client()
    r = client.get("/api/metrics")
    assert r.status_code == 200
    data = r.get_json()
    assert "cpu" in data and "ram" in data
