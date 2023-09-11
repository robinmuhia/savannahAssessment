from itsdangerous import TimestampSigner
import json
from base64 import b64encode
from app.config import settings

# fake session


def create_session_cookie(data) -> str:
    signer = TimestampSigner(str(settings.session_secret_key))

    return signer.sign(
        b64encode(json.dumps(data).encode('utf-8')),
    ).decode('utf-8')


def test_getitemsunauthorized(client):
    response = client.get("/api/items/", cookies={'session': create_session_cookie(
        {'user': {"name": "robin", "email": "robin@gmail.com"}})})
    assert response.status_code == 403


def test_getitemsauthorized(authorized_client):
    response = authorized_client.get("/api/items/", cookies={'session': create_session_cookie(
        {'user': {"name": "robin", "email": "robin@gmail.com"}})})
    assert response.status_code == 200


def test_orderitemsunauthorized(client):
    response = client.post("/api/items/", cookies={'session': create_session_cookie(
        {'user': {"name": "robin", "email": "robin@gmail.com"}})}, json={
            "name": "socks",
            "amount": "100"
    })
    assert response.status_code == 403


def test_orderitemsauthorized(authorized_client):
    # empty item name
    response = authorized_client.post("/api/items/", json={
        "name": "",
        "amount": "100"
    })
    assert response.status_code == 422
    # empty amount
    response = authorized_client.post("/api/items/", json={
        "name": "socks",
        "amount": ""
    })
    assert response.status_code == 422
    # empty name and amount
    response = authorized_client.post("/api/items/", json={
        "name": "",
        "amount": ""
    })
    assert response.status_code == 422
    # negative amount
    response = authorized_client.post("/api/items/", json={
        "name": "socks",
        "amount": "-1"
    })
    assert response.status_code == 422
    # amount is not int
    response = authorized_client.post("/api/items/", json={
        "name": "socks",
        "amount": "socks"
    })
    assert response.status_code == 422
    # no phone number
    response = authorized_client.post("/api/items/", cookies={'session': create_session_cookie(
        {'user': {"name": "mike", "email": "mike@gmail.com"}})}, json={
            "name": "socks",
            "amount": "100"
    })
    assert response.status_code == 406
    # all is good, runs locally but causes issues on github actions
    # response = authorized_client.post("/api/items/", cookies={'session': create_session_cookie(
    #     {'user': {"name": "robin", "email": "robin@gmail.com"}})}, json={
    #         "name": "socks",
    #         "amount": "100"
    # })
    assert response.status_code == 200
