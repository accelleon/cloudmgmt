from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from .route import Route


class App(BaseModel):
    guid: str
    urls: List[str]
    routes: List[Route]
    service_count: int
    service_names: List[str]
    running_instances: int
    name: str
    production: bool
    space_guid: str
    stack_guid: str
    buildpack: str
    detected_buildpack: str
    detected_buildpack_guid: Optional[str]
    environment_json: Dict[str, str]
    memory: int
    instances: int
    disk_quota: int
    state: str
    version: str
    command: str
    console: bool
    debug: Optional[bool]
    staging_task_id: str
    package_state: str
    health_check_type: str
    health_check_timeout: int
    health_check_http_endpoint: Optional[str]
    staging_failed_reason: Optional[str]
    staging_failed_description: Optional[str]
    diego: bool
    docker_image: Optional[str]
    package_updated_at: datetime
    detected_start_command: str
    enable_ssh: bool
    ports: Optional[Any]
