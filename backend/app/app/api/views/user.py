from typing import Any
from http import HTTPStatus

from fastapi import APIRouter, Request, Depends, HTTPException, Response

from app import model
from app.database import User
from app.api.core.cbv import cbv
from app.api.core.security import Permission
from app.api.services import UserService

router = APIRouter(prefix="/users")


@cbv(router)
class UserAPI:
    user: User = Depends(Permission("admin"))
    service: UserService = Depends()

    @router.get(
        "",
        response_model=model.UserSearchResponse,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
        },
    )
    async def get_users(
        self,
        request: Request,
        filter: model.UserFilter = Depends(),
        pagination: model.SearchQueryBase = Depends(),
    ):
        """
        Get a list of users filtered by query.
        """
        users, total = await self.service.search(filter=filter, pagination=pagination)
        return model.UserSearchResponse.from_results(
            pagination=pagination, results=users, total=total, request=request
        )

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
        self,
        *,
        user_in: model.CreateUser,
    ) -> Any:
        """
        Create a new user.
        """
        if await self.service.get_by_name(user_in.username):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="User with this username already exists",
            )

        return await self.service.create(data=user_in)

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
        self,
        *,
        user_id: int,
    ) -> Any:
        """
        Get a user by ID.
        """
        if user := await self.service.get(id=user_id):
            return user
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User with this ID not found",
        )

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
        self,
        user_id: int,
        *,
        user_in: model.UpdateUser,
    ) -> Any:
        """
        Update a user.
        """
        if not (user := await self.service.get(id=user_id)):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="User with this ID not found",
            )
        if user.id == self.service.user.id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="You cannot update your own user",
            )

        if user_in.username is not None and user_in.username != user.username:
            if await self.service.get_by_name(user_in.username):
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail="User with this username already exists",
                )

        # Cannot enable 2fa for another user
        if user_in.twofa_enabled and not user.twofa_enabled:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="You cannot enable 2fa for another user",
            )

        return await self.service.update(obj=user, data=user_in)

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
        self,
        user_id: int,
    ) -> Any:
        """
        Delete a user.
        """
        if user := await self.service.get(id=user_id):
            if user.id == self.service.user.id:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="You cannot delete your own user",
                )
            await self.service.delete(obj=user)
            return Response(status_code=HTTPStatus.NO_CONTENT)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User with this ID not found",
        )
