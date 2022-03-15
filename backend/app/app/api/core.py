from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import database, schema
from app.core import security
from app.core.config import configs
from app.database.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f'{configs.API_V1_STR}/login/token'
)

# Depend on a DB connection for an endpoint
def get_db() -> Generator:
    try:
        db_session = SessionLocal()
        yield db_session
    finally:
        db_session.close()

# Define various access restrictions we can Depends() on later

# Authenticated user
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> database.User:
    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = schema.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code = 401,
            detail = 'Must be authenticated'
        )
    user = database.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=400, detail='Token does not point to a valid user')
    return user

# Admin user
def get_admin_user(
    user: database.User = Depends(get_current_user)
) -> database.User:
    if not database.user.is_admin(user):
        raise HTTPException(status_code=403, detail='User does not have the required privileges to access this resource')
    return user