from typing import Optional, List
from pydantic import BaseModel

from .common import SearchQueryBase, SearchResponse


class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: Optional[bool] = None


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
    twofa_enabled: Optional[bool] = None
    twofa_code: Optional[str] = None


# DB specific things we *can* expose to the API
class User(UserBase):
    id: Optional[int] = None
    twofa_enabled: Optional[bool] = None
    twofa_uri: Optional[str] = None

    # TODO: We enable this but don't make use of it in the CRUD
    class Config:
        orm_mode = True


# Traits that shouldn't be exposed to the API
class UserDB(User):
    password: str  # Stored *hashed* password


class UserFilter(SearchQueryBase, UserBase):
    sort: Optional[str] = "username"


class UserSearchResponse(SearchResponse):
    results: List[User]
