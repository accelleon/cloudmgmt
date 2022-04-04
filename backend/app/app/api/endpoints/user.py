from typing import Any

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app import database, model
from app.api import core
from app.core.security import create_uri

router = APIRouter()


@router.get(
    "/me",
    response_model=model.User,
    responses={
        401: {"model": model.FailedResponse},
    },
)
def get_self(
    *,
    user: database.User = Depends(core.get_current_user),
) -> Any:
    return user


@router.post(
    "/me",
    response_model=model.User,
    responses={
        400: {"model": model.FailedResponse},
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
def update_self(
    *,
    user_in: model.UpdateUser,
    db: Session = Depends(core.get_db),
    user: database.User = Depends(core.get_current_user),
) -> Any:
    """
    Update own user.
    """
    if user_in.is_admin and not user.is_admin:
        raise HTTPException(403, "User may not perform this action")

    if user_in.username is not None and user_in.username != user.username:
        if database.user.get_by_username(db, username=user_in.username):
            raise HTTPException(409, "Username already exists")

    # Are we trying to enable 2fa? If so ensure our first code is valid
    if user_in.twofa_enabled and user_in.twofa_code:
        if not database.user.authenticate_twofa(db, user=user, otp=user_in.twofa_code):
            raise HTTPException(403, "Invalid TOTP code provided")

    newUser = database.user.update(db, db_obj=user, obj_in=user_in)
    resp: model.UserDB = newUser  # type: ignore

    # Generate our URI if needed
    if user_in.twofa_enabled and newUser.twofa_secret_tmp:
        resp.twofa_uri = create_uri(newUser.username, newUser.twofa_secret_tmp)

    return resp


@router.get(
    "",
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
    params = search.dict(exclude_unset=False)
    if total > query.per_page * (query.page + 1):
        params["page"] = search.page + 1
        resp.next = str(request.url.replace_query_params(**params))
    if query.page > 0:
        params["page"] = search.page - 1
        resp.prev = str(request.url.replace_query_params(**params))

    return resp


@router.post(
    "",
    status_code=201,
    response_model=model.User,
    responses={
        400: {"model": model.FailedResponse},
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
def create_user(
    *,
    user_in: model.CreateUser,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Create a new user.
    """
    if database.user.get_by_username(db, username=user_in.username):
        raise HTTPException(status_code=409, detail="Username already exists")

    newUser = database.user.create(db, obj_in=user_in)
    return newUser


@router.get(
    "/{user_id}",
    response_model=model.User,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
def get_user(
    *,
    user_id: int,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Get a user by ID.
    """
    user = database.user.get(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.patch(
    "/{user_id}",
    response_model=model.User,
    responses={
        400: {"model": model.FailedResponse},
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
def update_user(
    user_id: int,
    *,
    user_in: model.UpdateUser,
    db: Session = Depends(core.get_db),
    me: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Update a user.
    """
    # Get user we're updating
    user = database.user.get(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if user.id == me.id:
        raise HTTPException(403, "Use the /users/me endpoint to modify self")

    if user_in.username is not None and user_in.username != user.username:
        if database.user.get_by_username(db, username=user_in.username):
            raise HTTPException(409, "Username already exists")

    # Cannot enable 2fa for another user
    if user_in.twofa_enabled and not user.twofa_enabled:
        raise HTTPException(403, "Cannot enable 2FA for another user")

    newUser = database.user.update(db, db_obj=user, obj_in=user_in)
    return newUser


@router.delete(
    "/{user_id}",
    status_code=204,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
def delete_user(
    user_id: int,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Delete a user.
    """
    # Get user we're deleting
    user = database.user.delete(db, id=user_id)
    if not user:
        raise HTTPException(404, "User not found")
