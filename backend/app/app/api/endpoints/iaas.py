from typing import Any, List

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app import database, model
from app.api import core

router = APIRouter()


@router.get(
    "/",
    response_model=model.IaasSearchResponse,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
    },
)
async def get_providers(
    query: model.IaasSearchRequest = Depends(),
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
    request: Request,
) -> Any:
    filter = model.IaasFilter.parse_obj(query)
    search = model.common.SearchQueryBase.parse_obj(query)

    providers, total = await database.iaas.filter(
        db,
        filter=filter,
        offset=search.per_page * search.page,
        limit=search.per_page,
        sort=search.sort,
        order=search.order,
    )
    resp = model.IaasSearchResponse(
        **(search.dict(exclude_unset=False)), results=providers, total=total  # type: ignore
    )
    if total > search.per_page * (search.page + 1):
        params = search.dict(exclude_unset=False)
        params["page"] = search.page + 1
        resp.next = str(request.url.replace_query_params(**params))
    if search.page > 0:
        params = search.dict(exclude_unset=False)
        params["page"] = search.page - 1
        resp.prev = str(request.url.replace_query_params(**params))

    return resp


@router.get(
    "/{provider_id}",
    response_model=model.Iaas,
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
async def get_provider(
    provider_id: int,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
) -> Any:
    provider = await database.iaas.get(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.get(
    "/{provider_id}/accounts",
    response_model=List[model.Account],
    responses={
        401: {"model": model.FailedResponse},
        403: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
async def get_provider_accounts(
    provider_id: int,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_admin_user),
    request: Request,
) -> Any:
    iaas = await database.iaas.get(db, provider_id)
    if not iaas:
        raise HTTPException(status_code=404, detail="Provider not found")
    return iaas.accounts
