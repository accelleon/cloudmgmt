from typing import Optional
from pydantic import AnyUrl, validator, root_validator

from app.core.validators import validate_twofa
from app.model.user import UpdateUser, User


# Request sent to update your own user
class UpdateMe(UpdateUser):
    old_password: Optional[str] = None
    twofa_code: Optional[str] = None

    @validator("twofa_code")
    def validate_code(cls, v):
        return validate_twofa(v)

    @root_validator
    def validate_old_password(cls, values):
        old, new = values.get("old_password"), values.get("password")
        if new and not old:
            raise ValueError("Old password is required when changing password")
        if new and new == old:
            raise ValueError("Old password and new password cannot be the same")
        return values


# Response specific to the Me endpoint
class UpdateMeResponse(User):
    twofa_uri: Optional[AnyUrl] = None
