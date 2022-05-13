from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
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
    auth: model.AuthRequest,
    request: Request,
    db: Session = Depends(core.get_db),
) -> Any:
    """ """

    user = await database.user.authenticate_password(
        db, username=auth.username, password=auth.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username/password")

    if user.twofa_enabled:
        if auth.twofa_code is None:
            # User has 2fa enabled but didn't give us a code
            return JSONResponse(status_code=403, content=model.AuthResponse2Fa().dict())
        elif not await database.user.authenticate_twofa(
            db, user=user, otp=auth.twofa_code
        ):
            # User passed us the wrong 2fa code
            raise HTTPException(status_code=401, detail="Incorrect TOTP code provided")

    request.session["user_id"] = user.id
    request.session["is_admin"] = user.is_admin
    request.session["ip_address"] = request.client.host
    # If we're here, we've passed password and 2fa (if enabled)
    return {
        "access_token": security.create_token(user.id),
        "token_type": "bearer",
        "twofa_enabled": user.twofa_enabled,
    }


@router.post("/logout")
async def logout(
    request: Request,
) -> Any:
    """ """
    request.session.clear()
