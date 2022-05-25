from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starsessions import SessionMiddleware
from starsessions.backends.redis import RedisBackend
import uvicorn

from app.api.api import api_router
from app.core.config import configs


def generate_unique_id(route: APIRoute):
    return f"{route.name}"


app = FastAPI(
    title=configs.PROJECT_NAME,
    openapi_url="/api/openapi.json",
    generate_unique_id_function=generate_unique_id,
)

app.add_middleware(
    SessionMiddleware,
    backend=RedisBackend(configs.REDIS_DSN),
    max_age=0,  # session will expire after browser is closed
    secret_key=configs.SECRET_KEY,
    autoload=True,
    https_only=True,
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

app.include_router(api_router, prefix="/api")


def main():
    uvicorn.run("app.api_main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
