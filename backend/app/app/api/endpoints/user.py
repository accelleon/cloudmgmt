from typing import Any

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schema, database, model
from app.api import core
from app.core.security import create_uri

router = APIRouter()


@router.get(
    "/me",
    response_model=schema.user.User,
    responses={
        401: {"model": model.FailedResponse},
    },
)
def get_self(
    *,
    db: Session = Depends(core.get_db),
    user: database.User = Depends(core.get_current_user),
) -> Any:
    return user


@router.post(
    "/me",
    response_model=schema.user.User,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
    },
)
def update_self(
    *,
    user_in: schema.UpdateUser,
    db: Session = Depends(core.get_db),
    user: database.User = Depends(core.get_current_user),
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

    newUser = database.user.update(db, db_obj=user, obj_in=user_in)
    resp: schema.UserDB = newUser  # type: ignore

    # Generate our URI if needed
    if user_in.twofa_enabled and newUser.twofa_secret_tmp:
        resp.twofa_uri = create_uri(newUser.username, newUser.twofa_secret_tmp)

    return resp


@router.get(
    "/",
    response_model=model.UserSearchResponse,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
    },
)
def get_users(
    query: model.UserFilter = Depends(),
    *,
    db: Session = Depends(core.get_db),
    user: database.User = Depends(core.get_admin_user),
    request: Request,
):
    """
    Get a list of users filtered by query.
    """

    filter = model.UserBase.parse_obj(query)
    users, total = database.user.filter(
        db,
        filter=filter,
        offset=query.per_page * query.page,
        limit=query.per_page,
        sort=query.sort,
    )
    search = model.common.SearchQueryBase.parse_obj(query)
    resp = model.UserSearchResponse(
        **(search.dict(exclude_unset=False)), results=users, total=total  # type: ignore
    )
    if total > query.per_page * (query.page + 1):
        params = search.dict(exclude_unset=False)
        params["page"] = search.page + 1
        resp.next = str(request.url.replace_query_params(**params))
    if query.page > 0:
        params = search.dict(exclude_unset=False)
        params["page"] = search.page - 1
        resp.prev = str(request.url.replace_query_params(**params))

    return resp
