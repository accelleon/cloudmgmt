import sys
import inspect

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.logger import logger


class APIException(Exception):
    status_code = 500

    @classmethod
    async def handler(self, request: Request, exc: Exception):
        logger.exception(exc)
        return JSONResponse(
            status_code=self.status_code,
            content=jsonable_encoder({"detail": str(exc)}),
        )


class InvalidParameter(APIException):
    status_code = 400


class NotFound(APIException):
    status_code = 404

    def __init__(self, model, id):
        self.model = model
        super().__init__(f"{model.__name__} {id} does not exist")


class Conflict(APIException):
    status_code = 409

    def __init__(self, model, name):
        self.model = model
        self.name = name
        super().__init__(f"{model.__name__} with name {name} already exists")


def add_exception_handlers(app: FastAPI) -> None:
    for _, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(obj, APIException):
            print(f"Adding exception handler for {obj.__name__}")
            app.add_exception_handler(obj, obj.handler)
