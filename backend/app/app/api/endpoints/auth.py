from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import model, schema
from app.core import security

router = APIRouter(prefix='/login')

@router.post(
    '/',
    status_code = 200,
    responses = {
        401: schema.common.FailedResponse,
        403: schema.auth.AuthResponse2Fa,
    }
)
async def login(
    db: Session = Depends(deps.get_db),
    request: schema.auth.AuthRequest,
    response: Response
) -> Any:
    """
    """

    user = crud.user.authenticate(db, username=request.username, password=request.password)

    if not user:
        response.status_code = 401
        return schema.common.FailedResponse(message='Incorrect username/password')

    if user.twofa_enabled:
        if request.twofacode is None:
            # User has twofa enabled but didn't give us a code
            response.status_code = 403
            return schema.auth.AuthResponse2Fa()
        elif not user.authenticate_twofa(db, user=user, otp=request.twofacode):
            # User passed us the wrong 2fa code
            response.status_code = 401
            return schema.common.FailedResponse(message='Incorrect TOTP code provided')

    # If we're here, we've passed password and 2fa (if enabled)
    return {
        'access_token': security.create_token(user.id),
        'token_type': 'bearer',
        'twofa_enabled': user.twofa_enabled
    }