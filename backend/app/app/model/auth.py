from typing import Optional

from pydantic import BaseModel


class AuthRequest(BaseModel):
    username: str
    password: str
    twofa_code: Optional[str] = None


class AuthResponseOk(BaseModel):
    access_token: str
    token_type: str
    twofa_enabled: bool


class AuthResponse2Fa(BaseModel):
    twofa_required: bool = True
