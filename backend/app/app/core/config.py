from pathlib import Path
import json
import secrets
from typing import Any, Dict, List, Optional, Union

from urllib.parse import quote_plus
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, RedisDsn, validator


def json_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    Helper function to let us use a JSON file as a config source.
    """
    encoding = settings.__config__.env_file_encoding
    paths = [
        "config.json",
        "/etc/cloudcost/config.json",
    ]
    for path in paths:
        path = Path(path)
        if path.exists():
            return (
                json.loads(path.read_text(encoding=encoding))
            )
    return {}


class Configs(BaseSettings):
    # General settings
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    PROJECT_NAME: str

    # Allowed Origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Related to tokens
    SECRET_KEY: str = secrets.token_urlsafe(32)
    TOKEN_EXPIRES_MINUTES: int = 4 * 60

    # Database connection
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "cloudcost"
    POSTGRES_DSN: Optional[PostgresDsn] = None

    @validator("POSTGRES_DSN", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=quote_plus(values.get("POSTGRES_PASSWORD")),  # type: ignore
            host=values.get("POSTGRES_SERVER"),  # type: ignore
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    REDIS_SERVER: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DSN: Optional[RedisDsn] = None

    REDIS_2FA_DB: int = 1

    @validator("REDIS_DSN", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_SERVER"),
            port=str(values.get("REDIS_PORT")),
        )

    FIRST_USER_NAME: str = "admin"
    FIRST_USER_PASS: str

    class Config:
        case_sensitive = True
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                json_source,
                file_secret_settings,
            )


configs = Configs()  # type: ignore
