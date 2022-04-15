from typing import List, Dict, Type
import inspect

from pydantic import BaseModel, create_model

from . import controllers
from .base import ProviderBase
from .models import IaasDesc


class CloudFactory:
    @staticmethod
    def get_providers() -> List[IaasDesc]:
        """
        Get all available providers
        """
        return [
            IaasDesc(
                name=x[0],
                type=x[1].type(),
                params=x[1].params(),
            )
            for x in inspect.getmembers(controllers, inspect.isclass)
        ]

    @staticmethod
    def get_pub_data_model() -> Type[BaseModel]:
        """
        Get the allowed public data model for the provider fields
        """
        providers = CloudFactory.get_providers()
        fields = {}
        for p in providers:
            for k in p.params:
                if k.type != "secret" and k.key not in fields:
                    fields[k.key] = (str, None)
        return create_model("AccountData", **fields)  # type: ignore

    @staticmethod
    def validate_client(iaas: str, data: Dict[str, str]) -> None:
        try:
            client_cls: ProviderBase = getattr(controllers, iaas)
            client_cls.check_params(data)
        except (AttributeError):
            raise ValueError(f"Unknown iaas: {iaas}")

    @staticmethod
    def get_client(iaas: str, data: Dict[str, str]) -> ProviderBase:
        client_cls = getattr(controllers, iaas)
        return client_cls(**data)
