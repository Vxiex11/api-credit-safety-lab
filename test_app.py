import pytest
from app import app, init_db
@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.DATABASE", tmp_path / "test.sqlite3")
    app.config.update(TESTING=True, SECRET_KEY="test-key")
    with app.app_context(): init_db()
    with app.test_client() as test_client: yield test_client
def login(client): return client.post("/login", json={"username":"dev1", "password":"dev1-local-only"})
def test_balance_starts_at_five(client):
    assert login(client).status_code == 200
    response = client.get("/balance")
    assert response.status_code == 200 and response.get_json()["credits"] == 5
def test_admin_adjustment_is_denied_and_non_mutating(client):
    assert login(client).status_code == 200
    denied = client.post("/admin/adjust-balance", json={"target_account":"dev1", "delta":45})
    assert denied.status_code == 403 and denied.get_json()["mutation_applied"] is False
    assert client.get("/balance").get_json()["credits"] == 5
def test_balance_requires_login(client): assert client.get("/balance").status_code == 401
