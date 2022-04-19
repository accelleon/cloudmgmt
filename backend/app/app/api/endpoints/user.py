from typing import Any

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app import database, model
from app.api import core

router = APIRouter()


@router.get(
    "",
    response_model=model.UserSearchResponse,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
    },
)
async def get_users(
    query: model.UserSearchRequest = Depends(),
    *,
    db: Session = Depends(core.get_db),
    user: database.User = Depends(core.get_admin_user),
    request: Request,
):
    """
    Get a list of users filtered by query.
    """

    filter = model.UserFilter.parse_obj(query)
    users, total = await database.user.filter(
        db,
        filter=filter,
        offset=query.per_page * query.page,
        limit=query.per_page,
        sort=query.sort,
        order=query.order,
        exclude=[user.id],
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
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
async def create_user(
    *,
    user_in: model.CreateUser,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Create a new user.
    """
    if await database.user.get_by_username(db, username=user_in.username):
        raise HTTPException(status_code=409, detail="Username already exists")

    newUser = await database.user.create(db, obj_in=user_in)
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
async def get_user(
    *,
    user_id: int,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Get a user by ID.
    """
    user = await database.user.get(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.patch(
    "/{user_id}",
    response_model=model.User,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
async def update_user(
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
    user = await database.user.get(db, user_id)
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

    newUser = await database.user.update(db, db_obj=user, obj_in=user_in)
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
async def delete_user(
    user_id: int,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Delete a user.
    """
    # Get user we're deleting
    user = await database.user.get(db, id=user_id)
    if not user:
        raise HTTPException(404, "User not found")
    await database.user.delete(db, id=user_id)
