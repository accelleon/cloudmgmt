from typing import List

from pydantic import HttpUrl, SecretStr

from app.cloud.base import ProviderBase
from app.model.iaas import IaasType, IaasParam


class Jelastic(ProviderBase):
    endpoint: HttpUrl
    api_key: SecretStr

    @staticmethod
    def type() -> IaasType:
        return IaasType.PAAS

    @staticmethod
    def params() -> List[IaasParam]:
        return [
            IaasParam(key="endpoint", label="Endpoint", type="choice", choices=[
                "https://app.j.layershift.co.uk/",
                "https://app.paas.mamazala.com/",
                "https://app.jelastic.eapps.com/",
                "https://app.togglebox.cloud/",
                "https://app.cloudjiffy.com/",
                "https://app.env2.paas.ruh.cloudsigma.com/",
                "https://app.paas.massivegrid.com/",
                "https://app.mircloud.host/"
                ]),
            IaasParam(key="api_key", label="API Key", type="secret"),
        ]
