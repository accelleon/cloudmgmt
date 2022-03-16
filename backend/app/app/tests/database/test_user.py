from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import pyotp

from app import database
from app.core.security import verify_password
from app.schema.user import CreateUser, UpdateUser
from app.tests.utils import random_lower_string


def test_create_user(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = database.user.create(db, obj_in=user_in)
    assert user.username == username


def test_password_auth(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = database.user.create(db, obj_in=user_in)
    auth_user = database.user.authenticate_password(
        db, username=username, password=password
    )
    assert auth_user
    assert user.username == auth_user.username


def test_not_password_auth(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user = database.user.authenticate_password(db, username=username, password=password)
    assert user is None


def test_user_is_admin(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        is_admin=True,
        first_name="",
        last_name="",
    )
    user = database.user.create(db, obj_in=user_in)
    assert database.user.is_admin(db, user=user)


def test_user_not_is_admin(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = database.user.create(db, obj_in=user_in)
    assert not database.user.is_admin(db, user=user)


def test_get_user(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = database.user.create(db, obj_in=user_in)
    user2 = database.user.get(db, id=user.id)
    assert user2
    assert user.username == user2.username
    assert jsonable_encoder(user) == jsonable_encoder(user2)


def test_update_user(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    name = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name=name,
        last_name=name,
        is_admin=True,
    )
    new_password = random_lower_string()
    user = database.user.create(db, obj_in=user_in)
    user_in_update = UpdateUser(
        password=new_password,
    )
    database.user.update(db, db_obj=user, obj_in=user_in_update)
    user2 = database.user.get(db, id=user.id)
    # Normal verifications
    assert user2
    assert user.id == user2.id
    assert user.username == user2.username
    assert not verify_password(password, user2.password)
    assert verify_password(new_password, user2.password)
    # Make sure we're not modifying things we didn't want to
    assert database.user.is_admin(db, user=user2)


def test_enable_twofa(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = database.user.create(db, obj_in=user_in)
    update_data = UpdateUser(
        twofa_enabled=True,
    )
    user = database.user.update(db, db_obj=user, obj_in=update_data)
    # We fail this test if 2fa is marked enabled before the first code is validated or a temp secret isn't set
    assert not user.twofa_enabled
    assert user.twofa_secret_tmp

    old_secret = user.twofa_secret_tmp

    totp = pyotp.TOTP(user.twofa_secret_tmp)
    # Fail if we don't accept a 2fa code
    assert database.user.authenticate_twofa(db, user=user, otp=totp.now())

    user2 = database.user.update(db, db_obj=user, obj_in=update_data)
    # Now we fail if we don't mark 2fa enabled, remove the tmp secret and set the secret
    assert user2.twofa_enabled
    assert not user2.twofa_secret_tmp
    assert user2.twofa_secret == old_secret

    totp = pyotp.TOTP(user.twofa_secret)  # type: ignore
    # Fail if we don't accept a 2fa code
    assert database.user.authenticate_twofa(db, user=user, otp=totp.now())


def test_disable_twofa(db: Session) -> None:
    username = random_lower_string()
    password = random_lower_string()
    user_in = CreateUser(
        username=username,
        password=password,
        first_name="",
        last_name="",
    )
    user = database.user.create(db, obj_in=user_in)
    update_data = UpdateUser(
        twofa_enabled=True,
    )
    # We post this twice because of how we handle enabling 2fa, see test_enable_twofa()
    user = database.user.update(db, db_obj=user, obj_in=update_data)
    user = database.user.update(db, db_obj=user, obj_in=update_data)
    update_data = UpdateUser(
        twofa_enabled=False,
    )
    user = database.user.update(db, db_obj=user, obj_in=update_data)

    assert not user.twofa_enabled
    assert not user.twofa_secret
