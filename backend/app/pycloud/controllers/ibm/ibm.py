from typing import Dict, List, Optional
from datetime import datetime

from httpx import AsyncClient
from pydantic import parse_obj_as

from .auth import LoginResp
from .account import AccountResource, ListAccountResp
from .region import Region, ListRegionsResp, RegionResource


class IBMApi:
    headers: Dict[str, str]
    token: Optional[LoginResp]
    client: AsyncClient

    def __init__(self, api_key: str, client: AsyncClient = None):
        self.api_key = api_key
        self.client = client or AsyncClient()
        self.headers = {}
        self.token = None
        self.cf_token = None

    async def login(self) -> None:
        r = await self.client.post(
            "https://iam.cloud.ibm.com/identity/token",
            auth=("bx", "bx"),
            params={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key,
                "response_type": "cloud_iam",
            }
        )
        if r.status_code != 200:
            raise Exception(f"login failed: {r.status_code} {r.text}")
        self.token = LoginResp(**r.json())
        r = await self.client.post(
            "https://iam.cloud.ibm.com/identity/token",
            auth=("bx", "bx"),
            json={
                "grant_type": "refresh_token",
                "refresh_token": self.token.refresh_token,
                "response_type": "cloud_iam",
            },
        )
        self.headers.update({"Authorization": f"Bearer {self.token.access_token}"})

    async def refresh_auth(self) -> None:
        if not self.token:
            await self.login()
            return
        r = await self.client.post(
            "https://iam.cloud.ibm.com/identity/token",
            json={
                "refresh_token": self.token.refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if r.status_code != 200:
            raise Exception(f"refresh_auth failed: {r.text}")
        self.token = LoginResp(**r.json())
        self.headers.update({"Authorization": f"Bearer {self.token.access_token}"})

    async def ibm_check_token(self) -> None:
        if not self.token:
            await self.login()
        elif self.token.refresh_token_expiration < datetime.now():
            await self.login()
        elif self.token.expiration < datetime.now():
            await self.refresh_auth()

    async def get_accounts(self) -> List[AccountResource]:
        r = await self.client.get(
            "https://accounts.cloud.ibm.com/v1/accounts",
            headers=self.headers,
        )
        if r.status_code != 200:
            raise Exception(f"get_accounts failed: {r.text}")
        return AccountResource.map_model(ListAccountResp.parse_raw(r.text).resources, parent=self)

    async def get_regions(self) -> List[RegionResource]:
        r = await self.client.get(
            "https://mccp.us-south.cf.cloud.ibm.com/v2/regions",
            headers=self.headers,
        )
        if r.status_code != 200:
            raise Exception(f"get_regions failed: {r.text}")
        return RegionResource.map_model(parse_obj_as(ListRegionsResp, r.json()), parent=self)
