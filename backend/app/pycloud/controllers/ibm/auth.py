from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LoginResp(BaseModel):
    access_token: str
    refresh_token: str
    ims_user_id: int
    token_type: str
    expires_in: int
    expiration: datetime
    refresh_token_expiration: Optional[datetime]
    scope: str
    session_id: Optional[str]
