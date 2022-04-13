from typing import TYPE_CHECKING, List, Type, Dict, Any
import inspect

from pkg_resources import get_provider

from . import controllers
from app.model.iaas import IaasDesc
from app.cloud.base import ProviderBase


if TYPE_CHECKING:
    from app.model.account import Account


class CloudFactory:
    @staticmethod
    def get_providers() -> List[IaasDesc]:
        # Return names and parameters of all providers
        return [
            IaasDesc(
                name=x[0], type=x[1].type(), params=x[1].params(),
            )
            for x in inspect.getmembers(controllers, inspect.isclass)
        ]

    @staticmethod
    def _get_pub_fields() -> Dict[str, Any]:
        providers = CloudFactory.get_providers()
        resp = {}
        for p in providers:
            for k in p.params:
                if k.type != "secret" and k.key not in resp:
                    resp[k.key] = (str, None)
        return resp

    @staticmethod
    def get_client(account: 'Account') -> Type[ProviderBase]:
        try:
            client_cls = getattr(controllers, account.iaas.name)
            return client_cls.parse_obj(account.data)
        except AttributeError:
            raise ValueError(f"Unknown iaas: {account.iaas.name}")
