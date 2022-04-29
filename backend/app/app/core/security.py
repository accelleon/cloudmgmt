from datetime import datetime, timedelta
from math import ceil
from typing import Any, Union, Optional

import pyotp
from jose import jwt
from passlib.context import CryptContext

from app.core.config import configs

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    expires = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=configs.TOKEN_EXPIRES_MINUTES)
    )
    to_encode = {"exp": expires, "sub": str(subject), "iat": datetime.utcnow()}
    return jwt.encode(to_encode, configs.SECRET_KEY, algorithm=ALGORITHM)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Creates a Base32 secret key, compatible with most OTP apps
def create_secret() -> str:
    return pyotp.random_base32()


# Create a URI to make a QR code from
def create_uri(issuer: str, username: str, secret: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)


# Verify a TOTP code
def verify_totp(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code)


# Retrieve time remaining until the next TOTP code is valid
def totp_time_remaining(secret: str) -> int:
    totp = pyotp.TOTP(secret)
    return ceil(totp.interval - (datetime.now().timestamp() % totp.interval))
