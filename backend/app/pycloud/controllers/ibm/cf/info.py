from typing import Optional, Any

from pydantic import BaseModel


class Info(BaseModel):
    name: str
    build: str
    support: str
    version: int
    description: str
    authorization_endpoint: str
    token_endpoint: str
    min_cli_version: Optional[Any]
    min_recommended_cli_version: Optional[Any]
    app_ssh_endpoint: str
    app_ssh_host_key_fingerprint: str
    app_ssh_oauth_client: str
    doppler_logging_endpoint: str
    api_version: str
    osbapi_version: str
