from typing import Optional
from pydantic import BaseModel, validator

from app.core.validators import validate_password, validate_username
from .common import SearchQueryBase, SearchResponse


class UserFilter(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: Optional[bool] = None
    twofa_enabled: Optional[bool] = None


# Request sent to DB to create a user
# The password here is *plain text*
# Override the optional parameters that we require
class CreateUser(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str
    is_admin: bool = False

    @validator("username")
    def validate_username(cls, v):
        return validate_username(v)

    @validator("password")
    def validate_password(cls, v):
        return validate_password(v)


# Request sent to DB to update a user
class UpdateUser(UserFilter):
    password: Optional[str] = None
    twofa_enabled: Optional[bool] = None

    @validator("username")
    def validate_username(cls, v):
        return validate_username(v)

    @validator("password")
    def validate_password(cls, v):
        return validate_password(v)


# DB specific things we *can* expose to the API
class User(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    is_admin: bool
    twofa_enabled: bool

    # TODO: We enable this but don't make use of it in the CRUD
    class Config:
        orm_mode = True


class UserSearchRequest(SearchQueryBase, UserFilter):
    sort: Optional[str] = "username"


class UserSearchResponse(SearchResponse[User]):
    pass
