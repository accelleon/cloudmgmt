from typing import Any

from fastapi import APIRouter, Body, Depends, Response
from sqlalchemy.orm import Session

from app import schema, database
from app.core import security
from app.api import core

router = APIRouter()


@router.post("/login")
async def login(
    request: schema.auth.AuthRequest,
    response: Response,
    db: Session = Depends(core.get_db),
) -> Any:
    """ """

    user = database.user.authenticate_password(
        db, username=request.username, password=request.password
    )

    if not user:
        response.status_code = 401
        return schema.common.FailedResponse(message="Incorrect username/password")

    if user.twofa_enabled:
        if request.twofa_code is None:
            # User has 2fa enabled but didn't give us a code
            response.status_code = 403
            return schema.auth.AuthResponse2Fa()
        elif not database.user.authenticate_twofa(
            db, user=user, otp=request.twofa_code
        ):
            # User passed us the wrong 2fa code
            response.status_code = 401
            return schema.common.FailedResponse(message="Incorrect TOTP code provided")

    # If we're here, we've passed password and 2fa (if enabled)
    return {
        "access_token": security.create_token(user.id),
        "token_type": "bearer",
        "twofa_enabled": user.twofa_enabled,
    }
