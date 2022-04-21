from io import BytesIO
from typing import Optional
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession as Session
from openpyxl import Workbook

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
async def get_billing(
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
    billing, total = await database.billing.filter(
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
    "/export",
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            }
        },
        401: {"model": model.FailedResponse},
    },
)
async def export_billing(
    template: str = "default",
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    """
    Export billing periods as a spreadsheet.
    """
    wb = Workbook()
    ws = wb.active
    reports = await database.billing.get_cur_period(db)
    templateDb = await database.template.get_by_name(db, name="default")

    account_ids = {report.account_id: report for report in reports}

    ws.append(
        ["Provider", "Account", "Billing Start", "Billing End", "Cost", "Balance"]
    )

    for account_id in [order.account_id for order in templateDb.orders]:
        if account_id not in account_ids:
            continue
        report = account_ids[account_id]
        iaas = (
            f'{report.account.iaas.name} ({report.account.data["endpoint"]})'
            if "endpoint" in report.account.data
            else report.account.iaas.name
        )
        ws.append(
            [
                iaas,
                report.account.name,
                report.start_date.strftime("%Y-%m-%d"),
                report.end_date.strftime("%Y-%m-%d"),
                report.total,
                report.balance,
            ]
        )

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="filename.xlsx"'}
    return StreamingResponse(
        output,
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get(
    "/{id}",
    response_model=model.BillingPeriod,
    responses={
        401: {"model": model.FailedResponse},
        404: {"model": model.FailedResponse},
    },
)
async def get_billing_period(
    id: int,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    """
    Get a billing period by id.
    """

    billing = await database.billing.get(db, id)
    if not billing:
        raise HTTPException(status_code=404, detail="Billing period not found")

    return billing
