from typing import Any

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app import database, model
from app.api import core

router = APIRouter()


@router.get(
    "",
    response_model=model.AccountSearchResponse,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
    },
)
def get_accounts(
    query: model.AccountSearchRequest = Depends(),
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
    request: Request,
) -> Any:
    """
    Get a list of accounts filtered by query.
    """

    filter = model.AccountFilter.parse_obj(query)
    accounts, total = database.account.filter(
        db,
        filter=filter,
        offset=query.per_page * query.page,
        limit=query.per_page,
        sort=query.sort,
        order=query.order,
    )
    search = model.common.SearchQueryBase.parse_obj(query)
    resp = model.AccountSearchResponse(
        **(search.dict(exclude_unset=False)), results=accounts, total=total  # type: ignore
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
    response_model=model.Account,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        409: {"model": model.FailedResponse},
    },
)
def create_account(
    account: model.CreateAccount,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Create a new account.
    """
    if database.iaas.get_by_name(db, name=account.iaas) is None:
        raise HTTPException(status_code=422, detail="Iaas not found")

    if database.account.get_by_name(db, name=account.name, iaas=account.iaas):
        raise HTTPException(status_code=409, detail="Account name already exists")

    newAccount = database.account.create(db, obj_in=account)
    return newAccount


@router.get(
    "/{account_id}",
    response_model=model.Account,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
def get_account(
    account_id: int,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Get an account by id.
    """
    account = database.account.get(db, id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.patch(
    "/{account_id}",
    response_model=model.Account,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
def update_account(
    account_id: int,
    new: model.UpdateAccount,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    """
    Update an account.
    """
    account = database.account.get(db, id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    if new.name is not None and new.name != account.name:
        if database.account.get_by_name(db, name=account.name, iaas=account.iaas.name):
            raise HTTPException(status_code=409, detail="Account name already exists")

    updatedAccount = database.account.update(db, db_obj=account, obj_in=new)
    return updatedAccount


@router.delete(
    "/{account_id}",
    status_code=204,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
def delete_account(
    account_id: int,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> None:
    """
    Delete an account.
    """
    account = database.account.get(db, id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    database.account.delete(db, id=account_id)
    return None
