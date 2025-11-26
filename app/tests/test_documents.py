from io import BytesIO

def auth_header(client):
    client.post("/auth/register", json={
        "email": "user@example.com",
        "password": "strongpassword",
    })
    res = client.post(
        "/auth/token",
        data={
            "username": "user@example.com",
            "password": "strongpassword",
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_document(client):
    headers = auth_header(client)

    file_content = b"hello world"
    files = {
        "file": ("test.pdf", BytesIO(file_content), "application/pdf"),
    }
    data = {
        "title": "Contrato de prueba",
        "description": "Documento de ejemplo",
    }

    res = client.post(
        "/documents/upload",
        headers=headers,
        files=files,
        data=data,
    )

    assert res.status_code == 200
    body = res.json()
    assert body["filename"]
    assert body["status"] == "UPLOADED"