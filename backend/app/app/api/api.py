from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    me,
    user,
    account,
    iaas,
    billing,
)

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(me.router, prefix="/me", tags=["me"])
api_router.include_router(user.router, prefix="/users", tags=["user"])
api_router.include_router(iaas.router, prefix="/providers", tags=["provider"])
api_router.include_router(account.router, prefix="/accounts", tags=["account"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
