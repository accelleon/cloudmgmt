from typing import Optional

from pydantic import BaseModel


# Shared traits for both API and DB
# These are optional for the derived update class to avoid passing unnecessary data
class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: Optional[bool] = None
    twofa_enabled: Optional[bool] = None


# Request sent to DB to create a user
# The password here is *plain text*
# Override the optional parameters that we require
class CreateUser(UserBase):
    username: str
    first_name: str
    last_name: str
    password: str
    twofa_enabled: None = None  # Never enable 2fa on a new user


# Request sent to DB to update a user
class UpdateUser(UserBase):
    password: Optional[str] = None
    twofa_code: Optional[str] = None


# DB specific things we *can* expose to the API
class User(UserBase):
    id: Optional[int] = None
    twofa_secret_tmp: Optional[str] = None

    # Required by sqlalchemy
    class Config:
        orm_mode = True


# Traits that shouldn't be exposed to the API
class UserDB(User):
    password: str  # Stored *hashed* password
