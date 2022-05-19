from typing import Optional, List
from datetime import datetime

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app import database, model
from app.api import core

router = APIRouter()


@router.get(
    "/",
)
async def get_all_metrics(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    period: Optional[str] = None,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    end = end or datetime.utcnow()
    start = start or (end - relativedelta(day=1))
    iaas = await database.metric.filter(
        db, start=start, end=end, period=(period or "5min"), type=model.IaasType.IAAS
    )
    paas = await database.metric.filter(
        db, start=start, end=end, period=(period or "5min"), type=model.IaasType.PAAS
    )
    return [
        {"label": "IaaS Instances", "data": iaas.to_dict(orient="records")},
        {"label": "PaaS Instances", "data": paas.to_dict(orient="records")},
    ]


@router.get(
    "/{account}",
)
async def get_billing(
    account: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    *,
    db: Session = Depends(core.get_db),
    _: database.User = Depends(core.get_current_user),
):
    acct = await database.account.get(db, account)
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")
    start = start or (datetime.today() - relativedelta(day=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end = end or start + relativedelta(months=1)
    df = await database.metric.filter(
        db, account=acct, start=start, end=end, period="5min"
    )
    return {
        "label": f"{acct.name} ({acct.iaas.name})",
        "data": df.to_dict(orient="records"),
    }
