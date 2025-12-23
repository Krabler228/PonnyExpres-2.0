from fastapi.testclient import TestClient


def test_first_request_create_session_id(client: TestClient):
    response = client.get("/session-test")
    assert response.status_code == 200

    set_cookie_header = response.headers.get("set-cookie")
    assert set_cookie_header is not None
    assert "session_id=" in set_cookie_header

    body = response.json()
    assert "session_id" in body

    cookie_session_id = response.cookies.get("session_id")
    assert cookie_session_id is not None
    assert body["session_id"] == cookie_session_id


def test_second_request_uses_same_session_id(client: TestClient):
    response1 = client.get("/session-test")
    first_session_id = response1.cookies.get("session_id")
    assert first_session_id is not None

    response2 = client.get("/session-test")
    assert response2.status_code == 200

    body2 = response2.json()
    assert body2["session_id"] == first_session_id

    set_cookie_header2 = response2.headers.get("set-cookie")
    assert set_cookie_header2 is None


def test_session_cookie_flags(client: TestClient):
    response = client.get("/session-test")

    set_cookie_header = response.headers.get("set-cookie")
    assert set_cookie_header is not None
    assert "session_id=" in set_cookie_header
    assert "HttpOnly" in set_cookie_header
    assert "SameSite=lax" in set_cookie_header or "samesite=lax" in set_cookie_header
    assert "Secure" not in set_cookie_header
    assert "Path=/" in set_cookie_header or "Path=/" in set_cookie_header
