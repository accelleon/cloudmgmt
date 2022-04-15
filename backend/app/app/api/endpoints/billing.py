from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app import database, model
from app.api import core

router = APIRouter()


@router.get(
    "",
    response_model=model.BillingSearchResponse,
    responses={
        401: {"model": model.FailedResponse},
    },
)
def get_billing(
    query: model.BillingSearchRequest = Depends(),
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
    request: Request,
):
    """
    Get a list of billing period summaries filtered by query.
    """

    filter = model.BillingPeriodFilter.parse_obj(query)
    billing, total = database.billing.filter(
        db,
        filter=filter,
        offset=query.per_page * query.page,
        limit=query.per_page,
        sort=query.sort,
        order=query.order,
    )
    search = model.common.SearchQueryBase.parse_obj(query)
    resp = model.BillingSearchResponse(
        **(search.dict(exclude_unset=False)), results=billing, total=total  # type: ignore
    )
    params = search.dict(exclude_unset=False)
    if total > query.per_page * (query.page + 1):
        params["page"] = search.page + 1
        resp.next = str(request.url.replace_query_params(**params))
    if query.page > 0:
        params["page"] = search.page - 1
        resp.prev = str(request.url.replace_query_params(**params))

    return resp


@router.get(
    "/{id}",
    response_model=model.BillingPeriod,
    responses={
        401: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
def get_billing_period(
    id: int,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    """
    Get a billing period by id.
    """

    billing = database.billing.get(db, id)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing period not found")

    return billing
