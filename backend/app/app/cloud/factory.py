from typing import List, Type
import inspect

from . import controllers
from app.model.iaas import IaasDesc
from app.model.account import Account
from app.cloud.base import ProviderBase


class CloudFactory:
    @staticmethod
    def get_providers() -> List[IaasDesc]:
        # Return names of all classes in controllers
        return [
            IaasDesc(
                name=x[0], type=x[1].type(), params=[y for y in x[1].__fields__.keys()]
            )
            for x in inspect.getmembers(controllers, inspect.isclass)
        ]

    @staticmethod
    def get_client(account: Account) -> Type[ProviderBase]:
        try:
            client_cls = getattr(controllers, account.iaas.name)
            return client_cls.parse_obj(account.data)
        except AttributeError:
            raise ValueError(f"Unknown iaas: {account.iaas.name}")
