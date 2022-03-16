from typing import Optional

from pydantic import BaseModel


# Generic failure response
class FailedResponse(BaseModel):
    message: str
