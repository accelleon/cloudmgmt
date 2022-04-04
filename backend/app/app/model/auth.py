from typing import Optional

from pydantic import BaseModel, validator

from app.core.validators import validate_twofa


class AuthRequest(BaseModel):
    username: str
    password: str
    twofa_code: Optional[str] = None

    @validator("twofa_code")
    def validate_twofa_code(cls, v):
        if v is None:
            return v
        return validate_twofa(v)


class AuthResponseOk(BaseModel):
    access_token: str
    token_type: str
    twofa_enabled: bool


class AuthResponse2Fa(BaseModel):
    twofa_required: bool = True
