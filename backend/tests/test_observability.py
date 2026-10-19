from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.observability import request_logging_middleware


def test_request_id_is_present_and_is_not_echoed_from_untrusted_request():
    app = FastAPI()
    app.middleware("http")(request_logging_middleware)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-ID": "forged"})
        assert response.status_code == 200
        assert len(response.headers["X-Request-ID"]) == 32
        assert response.headers["X-Request-ID"] != "forged"
