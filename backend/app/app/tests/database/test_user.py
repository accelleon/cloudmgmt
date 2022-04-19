import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession as Session
import pyotp

from app import database
from app.core.security import verify_password
from app.model.user import CreateUser, UpdateUser, UserFilter
from app.model.me import UpdateMe
from app.tests.utils import random_username, random_password


@pytest.mark.asyncio
async def test_create_user(db: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = await database.user.create(db, obj_in=user_in)
    assert user.username == username


@pytest.mark.asyncio
async def test_password_auth(db: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = await database.user.create(db, obj_in=user_in)
    auth_user = await database.user.authenticate_password(
        db, username=username, password=password
    )
    assert auth_user
    assert user.username == auth_user.username


@pytest.mark.asyncio
async def test_not_password_auth(db: Session) -> None:
    username = random_username()
    password = random_password()
    user = await database.user.authenticate_password(
        db, username=username, password=password
    )
    assert user is None


@pytest.mark.asyncio
async def test_user_is_admin(db: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        is_admin=True,
        first_name="",
        last_name="",
    )
    user = await database.user.create(db, obj_in=user_in)
    assert database.user.is_admin(db, user=user)


@pytest.mark.asyncio
async def test_user_not_is_admin(db: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = await database.user.create(db, obj_in=user_in)
    assert not database.user.is_admin(db, user=user)


@pytest.mark.asyncio
async def test_get_user(db: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = await database.user.create(db, obj_in=user_in)
    user2 = await database.user.get(db, id=user.id)
    assert user2
    assert user.username == user2.username
    assert jsonable_encoder(user) == jsonable_encoder(user2)


@pytest.mark.asyncio
async def test_update_user(db: Session) -> None:
    username = random_username()
    password = random_password()
    name = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name=name,
        last_name=name,
        is_admin=True,
    )
    new_password = random_password()
    user = await database.user.create(db, obj_in=user_in)
    user_in_update = UpdateUser(
        password=new_password,
    )
    await database.user.update(db, db_obj=user, obj_in=user_in_update)
    user2 = await database.user.get(db, id=user.id)
    # Normal verifications
    assert user2
    assert user.id == user2.id
    assert user.username == user2.username
    assert not verify_password(password, user2.password)
    assert verify_password(new_password, user2.password)
    # Make sure we're not modifying things we didn't want to
    assert database.user.is_admin(db, user=user2)


@pytest.mark.asyncio
async def test_enable_twofa(db: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = await database.user.create(db, obj_in=user_in)
    update_data = UpdateUser(
        twofa_enabled=True,
    )
    user = await database.user.update(db, db_obj=user, obj_in=update_data)
    # We fail this test if 2fa is marked enabled before the first code is validated or a temp secret isn't set
    assert not user.twofa_enabled
    assert user.twofa_secret_tmp

    old_secret = user.twofa_secret_tmp

    totp = pyotp.TOTP(user.twofa_secret_tmp)
    # Fail if we don't accept a 2fa code
    assert database.user.authenticate_twofa(db, user=user, otp=totp.now())
    update_data = UpdateMe(twofa_enabled=True, twofa_code=totp.now())
    user2 = await database.user.update(db, db_obj=user, obj_in=update_data)
    # Now we fail if we don't mark 2fa enabled, remove the tmp secret and set the secret
    assert user2.twofa_enabled
    assert not user2.twofa_secret_tmp
    assert user2.twofa_secret == old_secret

    totp = pyotp.TOTP(user.twofa_secret)
    # Fail if we don't accept a 2fa code
    assert database.user.authenticate_twofa(db, user=user, otp=totp.now())


@pytest.mark.asyncio
async def test_disable_twofa(db: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = await database.user.create(db, obj_in=user_in)
    update_data = UpdateUser(
        twofa_enabled=True,
    )
    # We post this twice because of how we handle enabling 2fa, see test_enable_twofa()
    user = await database.user.update(db, db_obj=user, obj_in=update_data)
    user = await database.user.update(db, db_obj=user, obj_in=update_data)
    update_data = UpdateUser(
        twofa_enabled=False,
    )
    user = await database.user.update(db, db_obj=user, obj_in=update_data)

    assert not user.twofa_enabled
    assert not user.twofa_secret


@pytest.mark.asyncio
async def test_filter_user(db: Session) -> None:
    username = random_username()
    password = random_password()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
        is_admin=True,
    )
    user = await database.user.create(db, obj_in=user_in)
    filter = UserFilter(username=username)
    users, total = await database.user.filter(db, filter=filter)
    assert total == 1
    assert jsonable_encoder(user) == jsonable_encoder(users[0])
    filter = UserFilter(
        is_admin=True,
    )
    assert users
    for user in users:
        assert user.is_admin
