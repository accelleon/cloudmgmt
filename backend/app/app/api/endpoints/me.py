from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app import database, model
from app.api import core
from app.core.security import create_uri

router = APIRouter()


@router.get(
    "",
    response_model=model.User,
    responses={
        401: {"model": model.FailedResponse},
    },
)
async def get_self(
    *,
    user: database.User = Depends(core.get_current_user),
) -> Any:
    return user


@router.post(
    "",
    response_model=model.UpdateMeResponse,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
async def update_self(
    request: Request,
    *,
    user_in: model.UpdateMe,
    db: Session = Depends(core.get_db),
    user: database.User = Depends(core.get_current_user),
) -> Any:
    """
    Update own user.
    """
    if user_in.is_admin and not user.is_admin:
        raise HTTPException(403, "User may not perform this action")

    if user_in.old_password and not await database.user.authenticate_password(
        db, username=user.username, password=user_in.old_password
    ):
        raise HTTPException(403, "Incorrect password")

    if user_in.username is not None and user_in.username != user.username:
        if database.user.get_by_username(db, username=user_in.username):
            raise HTTPException(409, "Username already exists")

    # Are we trying to enable 2fa? If so ensure our first code is valid
    if user_in.twofa_enabled and user_in.twofa_code:
        if not database.user.authenticate_twofa(db, user=user, otp=user_in.twofa_code):
            raise HTTPException(403, "Invalid TOTP code provided")

    newUser = await database.user.update(db, db_obj=user, obj_in=user_in)
    resp: model.UserDB = newUser  # type: ignore

    # Generate our URI if needed
    if user_in.twofa_enabled and newUser.twofa_secret_tmp:
        resp.twofa_uri = create_uri(
            request.headers["Host"], newUser.username, newUser.twofa_secret_tmp
        )

    return resp
