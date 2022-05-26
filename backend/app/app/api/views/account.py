from typing import Any
from http import HTTPStatus

from fastapi import APIRouter, Request, Depends, HTTPException, Response

from app import model
from app.database import User
from app.api.core.cbv import cbv
from app.api.core.security import Permission
from app.api.services import AccountService

router = APIRouter(prefix="/accounts")


@cbv(router)
class AccountAPI:
    user: User = Depends(Permission("admin"))
    service: AccountService = Depends()

    @router.get(
        "",
        response_model=model.AccountSearchResponse,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
        },
    )
    async def get_accounts(
        self,
        request: Request,
        filter: model.AccountFilter = Depends(),
        pagination: model.SearchQueryBase = Depends(),
    ):
        """
        Get a list of accounts filtered by query.
        """
        accounts, total = await self.service.search(
            filter=filter, pagination=pagination
        )
        return model.AccountSearchResponse.from_results(
            pagination=pagination, results=accounts, total=total, request=request
        )

    @router.post(
        "",
        status_code=201,
        response_model=model.Account,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
            409: {"model": model.FailedResponse},
        },
    )
    async def create_account(
        self,
        *,
        account_in: model.CreateAccount,
    ) -> Any:
        """
        Create a new account.
        """
        return await self.service.create(data=account_in)

    @router.get(
        "/{account_id}",
        response_model=model.Account,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
            404: {"model": model.FailedResponse},
        },
    )
    async def get_account(
        self,
        account_id: int,
    ) -> Any:
        """
        Get an account by id.
        """
        return await self.service.get(id=account_id)

    @router.put(
        "/{account_id}",
        response_model=model.Account,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
            404: {"model": model.FailedResponse},
            409: {"model": model.FailedResponse},
        },
    )
    async def update_account(
        self,
        account_id: int,
        *,
        account_in: model.UpdateAccount,
    ) -> Any:
        """
        Update an account.
        """
        account = await self.service.get(id=account_id)
        return await self.service.update(obj=account, data=account_in)

    @router.delete(
        "/{account_id}",
        status_code=204,
        responses={
            401: {"model": model.FailedResponse},
            403: {"model": model.FailedResponse},
            404: {"model": model.FailedResponse},
        },
    )
    async def delete_account(
        self,
        account_id: int,
    ) -> Any:
        """
        Delete an account.
        """
        account = await self.service.get(id=account_id)
        await self.service.delete(obj=account)
