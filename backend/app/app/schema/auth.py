from typing import Optional

from pydantic import BaseModel

class AuthRequest(BaseModel):
    username: str
    password: str
    twofacode: Optional[str]

class AuthResponseOk(BaseModel):
    access_token: str
    token_type: str
    twofa_enabled: bool

class AuthResponse2Fa(BaseModel):
    twofarequired: bool = True

class TwoFaRequest(BaseModel):
    enableTwoFa: bool
    twofacode: Optional[str]

class TwoFaResponse(BaseModel):
    twofasecret: str