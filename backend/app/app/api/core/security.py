from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app import database, model
from app.core import security
from app.core.config import configs
from .db import get_db

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{configs.API_V1_STR}/login/token")

# Define various access restrictions we can Depends() on later
# Authenticated user
async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> database.User:
    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = model.TokenPayload(**payload)
        if not token_data.sub:
            raise jwt.JWTError
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=401, detail="Must be authenticated")
    user = await database.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=400, detail="Token does not point to a valid user"
        )
    return user


# Admin user
def get_admin_user(
    db: Session = Depends(get_db), user: database.User = Depends(get_current_user)
) -> database.User:
    if not database.user.is_admin(db, user=user):
        raise HTTPException(
            status_code=403,
            detail="User does not have the required privileges to access this resource",
        )
    return user


class Permission:
    permission: Optional[str]

    def __init__(self, permission: Optional[str] = None):
        self.permission = permission

    def __call__(self, user: database.User = Depends(get_current_user)):
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        print(self.permission, user.is_admin)
        if self.permission == "admin" and not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="User does not have the required privileges to access this resource",
            )
        return user
