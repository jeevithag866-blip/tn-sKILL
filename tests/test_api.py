from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["name"] == "LegalEase"


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_demo_mode_without_key(
    monkeypatch
):

    monkeypatch.setattr(
        "app.ai_core.gemini_generator.settings.gemini_api_key",
        "",
    )

    response = client.post(
        "/generate",
        json={
            "document_type": "NDA",

            "parties": (
                "Alice (Disclosing Party), "
                "Beta Ltd (Receiving Party)"
            ),

            "terms": (
                "Keep confidential; "
                "Return information on request"
            ),

            "dates": "1 January 2026",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["demo_mode"] is True

    assert "NDA" in data["document"]


def test_validation():

    response = client.post(
        "/generate",
        json={
            "document_type": "",

            "parties": "A",

            "terms": "B",

            "dates": "C",
        },
    )

    assert response.status_code == 422