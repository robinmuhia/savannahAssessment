from itsdangerous import TimestampSigner
import json
from base64 import b64encode
from app.config import settings

# fake session token


def create_session_cookie(data) -> str:
    signer = TimestampSigner(str(settings.session_secret_key))

    return signer.sign(
        b64encode(json.dumps(data).encode('utf-8')),
    ).decode('utf-8')


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "login" in response.text


def test_logout(client):
    response = client.get("/logout")
    assert response.status_code == 200


def test_changephonenum_unauthorized(client):
    response = client.post("/phone/", cookies={'session': create_session_cookie(
        {'user': {"name": "robin", "email": "robin@gmail.com"}})}, json={"phone_number": "0777014884"})
    assert response.status_code == 403


def test_changephonenum_authorized(authorized_client):
    # if number is not 9 in length
    response = authorized_client.post("/phone/", cookies={'session': create_session_cookie(
        {'user': {"name": "robin", "email": "robin@gmail.com"}})}, json={"phone_number": "7014884"})
    assert response.status_code == 422
    # if number is not numeric
    response = authorized_client.post("/phone/", cookies={'session': create_session_cookie(
        {'user': {"name": "robin", "email": "robin@gmail.com"}})}, json={"phone_number": "yesbana"})
    assert response.status_code == 422
    # if number is already in use
    response = authorized_client.post("/phone/", cookies={'session': create_session_cookie(
        {'user': {"name": "robin", "email": "robin@gmail.com"}})}, json={"phone_number": "0713014882"})
    assert response.status_code == 409
    # if number is correct
    response = authorized_client.post("/phone/", cookies={'session': create_session_cookie(
        {'user': {"name": "robin", "email": "robin@gmail.com"}})}, json={"phone_number": "0777014884"})
    assert response.status_code == 200
