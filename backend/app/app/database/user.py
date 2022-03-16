from typing import TYPE_CHECKING, Union, Dict, Any, Optional

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_secret, verify_totp
from app.database.base import Base, CRUDBase
from app.schema.user import CreateUser, UpdateUser


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_admin = Column(Boolean(), default=False, nullable=False)
    twofa_enabled = Column(Boolean(), default=False, nullable=False)
    twofa_secret = Column(String)
    twofa_secret_tmp = Column(String)

    def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r}, password={self.password!r})"


class CRUDUser(CRUDBase[User, CreateUser, UpdateUser]):
    # Class overrides
    def update(
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
            if update_data["twofa_enabled"] and db_obj.twofa_secret_tmp is None:
                # We're enabling twofa for the first time, create the secret, don't modify enabled yet
                update_data["twofa_secret_tmp"] = create_secret()
                del update_data["twofa_enabled"]
            elif update_data["twofa_enabled"] and db_obj.twofa_secret_tmp is not None:
                # We're modifying the user after successfully verifying the first OTP code
                update_data["twofa_secret"] = db_obj.twofa_secret_tmp
                update_data["twofa_secret_tmp"] = None
            else:
                # We're disabling twofa
                update_data["twofa_secret"] = None
                update_data["twofa_secret_tmp"] = None

        # Call our super
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def create(self, db: Session, *, obj_in: CreateUser) -> User:
        # Convert obj_in to a dict
        obj_in_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )
        # Hash our password
        obj_in_data["password"] = hash_password(obj_in_data["password"])
        # Create user object and add to DB
        db_obj = User(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        print(f"{db_obj!r}")
        return db_obj

    # Class specific
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def authenticate_password(
        self, db: Session, *, username: str, password: str  # Skip unnamed parameters
    ) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        # Return none if user not found or passwords don't match
        if user is None or not verify_password(password, user.password):
            return None
        return user

    def authenticate_twofa(self, db: Session, *, user: User, otp: str) -> bool:
        if user.twofa_secret is None and user.twofa_secret_tmp is None:
            # We shouldn't be here, we don't have 2fa enabled and we're not in the process of enabling it
            raise Exception("You tried verifying TOTP on a user without it enabled")
            return False

        # If 2fa is enabled, we're validating the user's existing 2fa
        # otherwise we're validating the user's first OTP
        secret = user.twofa_secret if user.twofa_enabled else user.twofa_secret_tmp
        return verify_totp(secret, otp)  # type: ignore

    def is_admin(
        self,
        db: Session,
        *,
        user: User,
    ) -> bool:
        return user.is_admin


# Create the actual CRUD object
user = CRUDUser(User)
