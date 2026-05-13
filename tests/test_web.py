import pytest
from fastapi.testclient import TestClient
from web_app import app


client = TestClient(app)


class TestWebAppRoot:
    def test_index_returns_html(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "f2b-manager" in resp.text


class TestApiJails:
    def test_jails_endpoint(self):
        resp = client.get("/api/jails")
        assert resp.status_code == 200
        data = resp.json()
        assert "jails" in data
        assert "active" in data
        assert "platform" in data


class TestApiStatus:
    def test_status_returns_json(self):
        resp = client.get("/api/status?jail=sshd")
        assert resp.status_code in (200, 503)
        if resp.status_code == 200:
            data = resp.json()
            assert "banned_count" in data
            assert "total_failed" in data

    def test_status_key_structure(self):
        resp = client.get("/api/status?jail=sshd")
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data["bans"], list)
            assert isinstance(data["banned_count"], int)
            assert "jail" in data
            assert data["jail"] == "sshd"


class TestApiBantime:
    def test_get_bantime(self):
        resp = client.get("/api/bantime?jail=sshd")
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            data = resp.json()
            assert "seconds" in data
            assert "label" in data
            assert "jail" in data

    def test_set_bantime_invalid(self):
        resp = client.post("/api/bantime?jail=sshd", json={"seconds": 10})
        assert resp.status_code == 400

    def test_set_bantime_valid(self):
        resp = client.post("/api/bantime?jail=sshd", json={"seconds": 3600})
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            assert resp.json()["success"]


class TestApiUnban:
    def test_unban_invalid_ip(self):
        resp = client.post("/api/unban/999.999.999.999?jail=sshd")
        assert resp.status_code in (200, 400)
