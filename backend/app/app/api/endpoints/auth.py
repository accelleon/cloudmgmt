from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app import database, model
from app.core import security
from app.api import core

router = APIRouter()


@router.post(
    "/login",
    response_model=model.AuthResponseOk,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.AuthResponse2Fa},
    },
)
async def login(
    request: model.AuthRequest,
    db: Session = Depends(core.get_db),
) -> Any:
    """ """

    user = await database.user.authenticate_password(
        db, username=request.username, password=request.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username/password")

    if user.twofa_enabled:
        if request.twofa_code is None:
            # User has 2fa enabled but didn't give us a code
            return JSONResponse(status_code=403, content=model.AuthResponse2Fa().dict())
        elif not database.user.authenticate_twofa(
            db, user=user, otp=request.twofa_code
        ):
            # User passed us the wrong 2fa code
            raise HTTPException(status_code=401, detail="Incorrect TOTP code provided")

    # If we're here, we've passed password and 2fa (if enabled)
    return {
        "access_token": security.create_token(user.id),
        "token_type": "bearer",
        "twofa_enabled": user.twofa_enabled,
    }
