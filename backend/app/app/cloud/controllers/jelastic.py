from pydantic import HttpUrl, SecretStr

from app.cloud.base import ProviderBase
from app.model.iaas import IaasType


class Jelastic(ProviderBase):
    endpoint: HttpUrl
    api_key: SecretStr

    @staticmethod
    def type() -> IaasType:
        return IaasType.PAAS
