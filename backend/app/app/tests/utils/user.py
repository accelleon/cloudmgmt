from typing import Dict, Tuple

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import database
from app.core.config import configs
from app.database.user import User
from app.schema.user import CreateUser, UpdateUser
from app.tests.utils import random_lower_string


def user_authenticate_headers(
    *, client: TestClient, username: str, password: str
) -> Dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{configs.API_V1_STR}/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def admin_user_headers(client: TestClient) -> Dict[str, str]:
    return user_authenticate_headers(
        client=client,
        username=configs.FIRST_USER_NAME,
        password=configs.FIRST_USER_PASS,
    )


def create_random_user(db: Session) -> Tuple[str, str]:
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    database.user.create(db, obj_in=user_in)
    return username, password


def create_user_twofa(db: Session) -> Tuple[str, str, str]:
    username, password = create_random_user(db)
    # Do some hackery to get a user in the right state
    update_data = UpdateUser(
        twofa_enabled=True
    )
    user = database.user.get_by_username(db, username=username)
    user = database.user.update(db=db, db_obj=user, obj_in=update_data) # type: ignore
    user = database.user.update(db=db, db_obj=user, obj_in=update_data) # type: ignore
    return username, password, user.twofa_secret


def auth_headers_random(*, client: TestClient, db: Session) -> Dict[str, str]:
    username, password = create_random_user(db)
    return user_authenticate_headers(
        client=client, username=username, password=password
    )
