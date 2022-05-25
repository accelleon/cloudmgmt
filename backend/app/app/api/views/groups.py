from fastapi import APIRouter, Request, Depends, HTTPException, Response

from app import model
from app.database import User
from app.api.core.cbv import cbv
from app.api.core.security import Permission
from app.api.services import GroupService

router = APIRouter(prefix="/groups")


@cbv(router)
class GroupAPI:
    user: User = Depends(Permission("admin"))
    service: GroupService = Depends()

    @router.get(
        "",
        response_model=model.GroupSearchResponse,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
        },
    )
    async def get_groups(
        self,
        request: Request,
        filter: model.FilterGroup = Depends(),
        pagination: model.SearchQueryBase = Depends(),
    ):
        """
        Get a list of groups filtered by query.
        """
        groups, total = await self.service.search(filter=filter, pagination=pagination)
        return model.GroupSearchResponse.from_results(
            pagination=pagination, results=groups, total=total, request=request
        )

    @router.post(
        "",
        status_code=201,
        response_model=model.Group,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
            409: {"model": model.FailedResponse},
        },
    )
    async def create_group(
        self,
        *,
        group_in: model.CreateGroup,
    ):
        """
        Create a new group.
        """
        if await self.service.get_by_name(name=group_in.name):
            raise HTTPException(status_code=409, detail="Group already exists")
        return await self.service.create(data=group_in)

    @router.get(
        "/{group_id}",
        response_model=model.Group,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
            404: {"model": model.FailedResponse},
        },
    )
    async def get_group(
        self,
        group_id: int,
    ):
        """
        Get a group by id.
        """
        if group := await self.service.get(id=group_id):
            return group
        raise HTTPException(status_code=404, detail="Group not found")

    @router.put(
        "/{group_id}",
        response_model=model.Group,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
            404: {"model": model.FailedResponse},
            409: {"model": model.FailedResponse},
        },
    )
    async def update_group(
        self,
        group_id: int,
        *,
        group_in: model.UpdateGroup,
    ):
        """
        Update a group by id.
        """
        if group := await self.service.get(id=group_id):
            if group_in.name and group.name != group_in.name:
                if await self.service.get_by_name(name=group_in.name):
                    raise HTTPException(status_code=409, detail="Group already exists")
            return await self.service.update(obj=group, data=group_in)
        raise HTTPException(status_code=404, detail="Group not found")

    @router.delete(
        "/{group_id}",
        status_code=204,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
            404: {"model": model.FailedResponse},
        },
    )
    async def delete_group(
        self,
        group_id: int,
    ):
        """
        Delete a group by id.
        """
        if group := await self.service.get(id=group_id):
            if group.accounts:
                raise HTTPException(
                    status_code=400,
                    detail="May not delete group with assigned accounts",
                )
            await self.service.delete(obj=group)
            return Response(status_code=204)
        raise HTTPException(status_code=404, detail="Group not found")
