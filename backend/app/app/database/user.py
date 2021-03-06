from typing import Union, Dict, Any, Optional

from sqlalchemy import select, Boolean, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.database.session import redis_2fa
from app.core.security import (
    hash_password,
    verify_password,
    create_secret,
    verify_totp,
    totp_time_remaining,
)
from app.database.base import Base, CRUDBase
from app.model import CreateUser, UpdateUser, UserFilter


class User(Base):
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, index=True, nullable=False)
    password: str = Column(String, nullable=False)
    first_name: str = Column(String, nullable=False)
    last_name: str = Column(String, nullable=False)
    is_admin: bool = Column(Boolean, default=False, nullable=False)
    twofa_enabled: bool = Column(Boolean, default=False, nullable=False)
    twofa_secret: str = Column(String)
    twofa_secret_tmp: str = Column(String)

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r}, password={self.password!r})"


class CRUDUser(CRUDBase[User, CreateUser, UpdateUser, UserFilter]):
    # Class overrides
    async def update(
        self,
        db: Session,
        *,  # Skip unnamed parameters
        db_obj: User,
        obj_in: Union[UpdateUser, Dict[str, Any]],
    ) -> User:
        # Convert obj_in to a dict if it isn't already
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )

        # Hash the plaintext password if we're updating it
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])

        # Are we modifying the twofa_enabled field?
        if (
            "twofa_enabled" in update_data
            and update_data["twofa_enabled"] != db_obj.twofa_enabled
        ):
            if update_data["twofa_enabled"] and "twofa_code" not in update_data:
                # We asked for it to be enabled but didn't provide a code
                # We're enabling for the first time
                update_data["twofa_secret_tmp"] = create_secret()
                del update_data["twofa_enabled"]
            elif update_data["twofa_enabled"] and db_obj.twofa_secret_tmp is not None:
                # We're modifying the user after successfully verifying the first OTP code
                update_data["twofa_secret"] = db_obj.twofa_secret_tmp
                update_data["twofa_secret_tmp"] = None
        if "twofa_enabled" in update_data and not update_data["twofa_enabled"]:
            # We're disabling 2fa
            update_data["twofa_secret"] = None
            update_data["twofa_secret_tmp"] = None

        # Call our super
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def create(self, db: Session, *, obj_in: CreateUser) -> User:
        # Convert obj_in to a dict
        obj_in_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )
        # Hash our password
        obj_in_data["password"] = hash_password(obj_in_data["password"])
        # Create user object and add to DB
        db_obj = User(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # Class specific
    async def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return (
            (await db.execute(select(User).where(User.username == username)))
            .scalars()
            .first()
        )

    async def authenticate_password(
        self, db: Session, *, username: str, password: str  # Skip unnamed parameters
    ) -> Optional[User]:
        user = await self.get_by_username(db, username=username)
        # Return none if user not found or passwords don't match
        if user is None or not verify_password(password, user.password):
            return None
        return user

    async def authenticate_twofa(self, db: Session, *, user: User, otp: str) -> bool:
        if user.twofa_secret is None and user.twofa_secret_tmp is None:
            # We shouldn't be here, we don't have 2fa enabled and we're not in the process of enabling it
            raise Exception("You tried verifying TOTP on a user without it enabled")

        redis_key = f"{user.username}:{otp}"
        if await redis_2fa.get(redis_key):
            # We've already used this code
            return False

        # If 2fa is enabled, we're validating the user's existing 2fa
        # otherwise we're validating the user's first OTP
        secret = user.twofa_secret if user.twofa_enabled else user.twofa_secret_tmp
        await redis_2fa.set(redis_key, "1", ex=totp_time_remaining(secret))

        return verify_totp(secret, otp)

    def is_admin(
        self,
        db: Session,
        *,
        user: User,
    ) -> bool:
        return user.is_admin


# Create the actual CRUD object
user = CRUDUser(User)
