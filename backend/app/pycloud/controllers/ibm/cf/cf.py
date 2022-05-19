from typing import TYPE_CHECKING, Dict, Optional, List
from base64 import b64encode

from httpx import AsyncClient

from .auth import LoginResp
from .organization import ListOrganiztionsResp, OrganizationResource

if TYPE_CHECKING:
    from ..ibm import IBMApi
    from ..region import RegionResource, Region


class CloudFoundry:
    ibm: 'IBMApi'
    region: 'Region'
    headers: Dict[str, str]
    token: Optional[LoginResp]
    client: AsyncClient

    def __init__(self, region: "RegionResource"):
        self.ibm = region.parent
        self.region = region.me
        self.apikey = self.ibm.api_key
        self.client = self.ibm.client
        self.headers = {}

    async def login(self) -> None:
        r = await self.ibm.client.post(
            f"https://iam.cloud.ibm.com/cloudfoundry/login/{self.region.region}/oauth/token",
            headers={
                "Authorization": f"Basic {b64encode('cf:'.encode('utf-8')).decode('utf-8')}",
            },
            params={
                "grant_type": "iam_token",
                "iam_token": self.ibm.token.access_token,
            }
        )
        if r.status_code != 200:
            raise Exception(f"login failed: {r.status_code} {r.text}")
        self.token = LoginResp(**r.json())
        self.headers.update({"Authorization": f"Bearer {self.token.access_token}"})

    async def get_organizations(self) -> List[OrganizationResource]:
        r = await self.ibm.client.get(
            f"{self.region.cf_api}/v2/organizations",
            headers=self.headers,
        )
        if r.status_code != 200:
            raise Exception(f"get_organizations failed: {r.text}")
        return OrganizationResource.map_model(ListOrganiztionsResp(**r.json()).resources, parent=self, region=self.region)
