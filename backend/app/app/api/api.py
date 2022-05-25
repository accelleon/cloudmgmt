from fastapi import APIRouter

from app.api import endpoints, views

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(endpoints.auth.router, tags=["login"])
v1_router.include_router(endpoints.me.router, prefix="/me", tags=["me"])
v1_router.include_router(views.user.router, tags=["user"])
v1_router.include_router(endpoints.iaas.router, prefix="/providers", tags=["provider"])
v1_router.include_router(endpoints.account.router, prefix="/accounts", tags=["account"])
v1_router.include_router(endpoints.billing.router, prefix="/billing", tags=["billing"])
v1_router.include_router(
    endpoints.template.router, prefix="/template", tags=["template"]
)
v1_router.include_router(endpoints.metric.router, prefix="/metric", tags=["metric"])

api_router = APIRouter()
api_router.include_router(v1_router)
