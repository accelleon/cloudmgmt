from http.client import HTTPException
from typing import Any

from fastapi import APIRouter, Body, Depends, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import schema, database
from app.api import core

router = APIRouter()


@router.get("/me", response_model=schema.user.User)
def get_self(
    *,
    db: Session = Depends(core.get_db),
    user: database.User = Depends(core.get_current_user)
) -> Any:
    return user


@router.post("/me", response_model=schema.user.User)
def update_self(
    *,
    user_in: schema.UpdateUser,
    db: Session = Depends(core.get_db),
    user: database.User = Depends(core.get_current_user)
) -> Any:
    """
    Update own user.
    """
    if user_in.is_admin and not user.is_admin:
        raise HTTPException(403, "User may not perform this action")

    # Are we trying to enable 2fa? If so ensure our first code is valid
    if user_in.twofa_enabled and user_in.twofa_code:
        if not database.user.authenticate_twofa(db, user=user, otp=user_in.twofa_code):
            raise HTTPException(403, "Invalid TOTP code provided")

    user = database.user.update(db, db_obj=user, obj_in=user_in)
    return user
