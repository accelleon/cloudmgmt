from typing import Dict, Tuple, Optional

from httpx import AsyncClient as TestClient
from sqlalchemy.ext.asyncio import AsyncSession as Session
import pyotp

from app import database
from app.core.config import configs
from app.model.user import CreateUser, UpdateUser
from app.model.me import UpdateMe
from app.tests.utils import random_username, random_password


async def user_authenticate_headers(
    client: TestClient, username: str, password: str, twofa_code: Optional[str] = None
) -> Dict[str, str]:
    data = {"username": username, "password": password, "twofa_code": twofa_code}
    r = await client.post(f"{configs.API_V1_STR}/login", json=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


async def admin_user_headers(client: TestClient) -> Dict[str, str]:
    return await user_authenticate_headers(
        client=client,
        username=configs.FIRST_USER_NAME,
        password=configs.FIRST_USER_PASS,
    )


async def create_random_user(db: Session) -> Tuple[str, str, int]:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = await database.user.create(db, obj_in=user_in)
    return username, password, user.id


async def create_user_twofa(db: Session) -> Tuple[str, str, str]:
    username, password, _ = await create_random_user(db)
    # Do some hackery to get a user in the right state
    update_data = UpdateMe(twofa_enabled=True)
    user = await database.user.get_by_username(db, username=username)
    user = await database.user.update(db=db, db_obj=user, obj_in=update_data)  # type: ignore
    update_data = UpdateMe(
        twofa_enabled=True,
        twofa_code=pyotp.TOTP(user.twofa_secret_tmp).now(),
    )
    user = await database.user.update(db=db, db_obj=user, obj_in=update_data)  # type: ignore
    return username, password, user.twofa_secret


async def auth_headers_random(client: TestClient, db: Session) -> Dict[str, str]:
    username, password, _ = await create_random_user(db)
    return await user_authenticate_headers(
        client=client, username=username, password=password
    )


async def auth_headers_username(
    db: Session,
    client: TestClient,
    username: str,
) -> Dict[str, str]:
    password = random_password()
    user = await database.user.get_by_username(db, username=username)
    if not user:
        create = CreateUser(
            username=username, password=password, first_name="", last_name=""
        )
        user = await database.user.create(db, obj_in=create)
    else:
        update = UpdateUser(password=password)
        user = await database.user.update(db, db_obj=user, obj_in=update)

    return await user_authenticate_headers(
        client=client, username=username, password=password
    )
