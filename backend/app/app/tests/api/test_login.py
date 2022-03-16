from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pyotp

from app.core.config import configs
from app.tests.utils.user import create_user_twofa

def test_login(client: TestClient) -> None:
    login_data = {
        "username": configs.FIRST_USER_NAME,
        "password": configs.FIRST_USER_PASS,
    }
    r = client.post(f"{configs.API_V1_STR}/login", json=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]

def test_login_twofa(client: TestClient, db: Session) -> None:
    username, password, twofa_secret = create_user_twofa(db=db)
    login_data = {
        'username': username,
        'password': password
    }
    r = client.post(f'{configs.API_V1_STR}/login', json=login_data)
    js = r.json()
    # We should get a 403 and json containing `twofarequired`
    assert r.status_code == 403
    assert 'twofarequired' in js
    assert js['twofarequired']
    # Auth with token again
    login_data['twofacode'] = pyotp.TOTP(twofa_secret).now()
    r = client.post(f'{configs.API_V1_STR}/login', json=login_data)
    js = r.json()
    # This should be successful
    assert r.status_code == 200
    assert 'access_token' in js
    assert js['access_token']