from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import configs


def generate_unique_id(route: APIRoute):
    return f"{route.name}"


app = FastAPI(
    title=configs.PROJECT_NAME,
    openapi_url=f"{configs.API_V1_STR}/openapi.json",
    generate_unique_id_function=generate_unique_id,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS]
    if configs.BACKEND_CORS_ORIGINS
    else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=configs.API_V1_STR)
