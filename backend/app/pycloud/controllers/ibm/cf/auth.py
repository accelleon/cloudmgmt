from pydantic import BaseModel


class LoginResp(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    id_token: str
    expires_in: int
    scope: str
    jti: str
