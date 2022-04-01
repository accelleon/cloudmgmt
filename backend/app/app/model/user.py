from typing import Optional, List

from app.schema.user import UserBase, User
from .common import SearchQueryBase, SearchResponse


class UserFilter(SearchQueryBase, UserBase):
    sort: Optional[str] = "username"


class UserSearchResponse(SearchResponse):
    results: List[User]
