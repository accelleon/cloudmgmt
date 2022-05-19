from pydantic import BaseModel

from .common import Metadata


class QuotaEntity(BaseModel):
    name: str
    non_basic_services_allowed: bool
    total_services: int
    total_routes: int
    total_private_domains: int
    memory_limit: int
    trial_db_allowed: bool
    instance_memory_limit: int
    app_instance_limit: int
    app_task_limit: int
    total_service_keys: int
    total_reserved_route_ports: int


class QuotaDefinition(BaseModel):
    metadata: Metadata
    entity: QuotaEntity
