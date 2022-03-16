import secrets
from typing import Any, Dict, List, Optional, Union

from urllib.parse import quote_plus
from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, PostgresDsn, validator


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
    TOKEN_EXPIRES_MINUTES: int = 60

    # Database connection
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: Optional[PostgresDsn] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=quote_plus(values.get("POSTGRES_PASSWORD")),  # type: ignore
            host=values.get("POSTGRES_SERVER"),  # type: ignore
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    FIRST_USER_NAME: str = "admin"
    FIRST_USER_PASS: str

    class Config:
        case_sensitive = True


configs = Configs()  # type: ignore
