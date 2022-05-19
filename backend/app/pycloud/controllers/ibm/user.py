from typing import List, Optional

from pydantic import BaseModel


class Linkage(BaseModel):
    origin: str
    id: str


class User(BaseModel):
    id: str
    iam_id: str
    realm: str
    user_id: str
    firstname: str
    lastname: str
    state: str
    sub_state: str
    email: str
    phonenumber: str
    altphonenumber: str
    photo: str
    account_id: str
    linkages: Optional[List[Linkage]]
