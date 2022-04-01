from pydantic import BaseModel


# Generic failure response
class FailedResponse(BaseModel):
    detail: str
