from typing import Dict, Tuple, Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pyotp

from app import database
from app.core.config import configs
from app.model.user import CreateUser, UpdateUser, UpdateSelf
from app.tests.utils import random_username, random_password


def user_authenticate_headers(
    client: TestClient, username: str, password: str, twofa_code: Optional[str] = None
) -> Dict[str, str]:
    data = {"username": username, "password": password, "twofa_code": twofa_code}
    r = client.post(f"{configs.API_V1_STR}/login", json=data)
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


def create_random_user(db: Session) -> Tuple[str, str, int]:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = database.user.create(db, obj_in=user_in)
    return username, password, user.id


def create_user_twofa(db: Session) -> Tuple[str, str, str]:
    username, password, _ = create_random_user(db)
    # Do some hackery to get a user in the right state
    update_data = UpdateSelf(twofa_enabled=True)
    user = database.user.get_by_username(db, username=username)
    user = database.user.update(db=db, db_obj=user, obj_in=update_data)  # type: ignore
    update_data = UpdateSelf(
        twofa_enabled=True,
        twofa_code=pyotp.TOTP(user.twofa_secret_tmp).now(),  # type: ignore
    )
    user = database.user.update(db=db, db_obj=user, obj_in=update_data)  # type: ignore
    return username, password, user.twofa_secret  # type: ignore


def auth_headers_random(client: TestClient, db: Session) -> Dict[str, str]:
    username, password, _ = create_random_user(db)
    return user_authenticate_headers(
        client=client, username=username, password=password
    )


def auth_headers_username(
    db: Session,
    client: TestClient,
    username: str,
) -> Dict[str, str]:
    password = random_password()
    user = database.user.get_by_username(db, username=username)
    if not user:
        create = CreateUser(
            username=username, password=password, first_name="", last_name=""
        )
        user = database.user.create(db, obj_in=create)
    else:
        update = UpdateUser(password=password)
        user = database.user.update(db, db_obj=user, obj_in=update)

    return user_authenticate_headers(
        client=client, username=username, password=password
    )
