from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import database
from app.core.config import configs
from app.schema.user import CreateUser, UpdateUser
from app.tests.utils import random_lower_string

def user_authenticate_headers(
    *,
    client: TestClient,
    username: str,
    password: str
) -> Dict[str, str]:
    data = {
        'username': username,
        'password': password
    }

    r = client.post(f'{configs.API_V1_STR}/login', data=data)
    response = r.json()
    auth_token = response['access_token']
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    return headers

def create_random_user(db: Session) -> User:
    username = random_lower_string()
    password = random_upper_string()
    user_in = CreateUser(
        username = username,
        password = password,
        first_name = '',
        last_name = '',
    )
    user = database.user.create(db=db, user_in=user_in)

def create_user_twofa(db: Session) -> User:
    user = create_random_user(db)
    # Do some hackery to get a user in the right state
    update_data = {
        'twofa_enabled': True,
    }
    user = database.user.update(db=db, user=user, obj_in=update_data)
    if not user.twofa_secret_tmp:
        return None
    
    