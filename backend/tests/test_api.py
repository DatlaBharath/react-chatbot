def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_list_messages(client):
    r = client.post("/api/messages", json={"content": "hello"})
    assert r.status_code == 201
    assert r.json()["content"] == "hello"

    r = client.get("/api/messages")
    assert r.status_code == 200
    assert [m["content"] for m in r.json()] == ["hello"]


def test_rejects_empty_message(client):
    r = client.post("/api/messages", json={"content": ""})
    assert r.status_code == 422
