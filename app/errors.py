from typing import Any, Union, List

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from dataclasses import dataclass


class Test:
    """
    asdf
    """

    # x: str
    # y: str

    def __init__(self, x: str, y: str):
        self.x = x
        self.y = y


Test("a", "b")
# @dataclass
class KYCProviderError(Exception):
    """
    Parent class for all KYC Provider errors
    """

    message: str
    status: int
    code: str
    type: str
    extra: Any

    def __init__(
        self,
        message: str,
        status: int = 424,
        code: str = "kyc_error",
        type: str = "KYC Error",
        extra: Any = None,
    ):
        self.message: str = message
        self.status: int = status
        self.code: str = code
        self.type = type
        self.extra = extra

        self.resp = {
            "message": message,
            "status": status,
            "code": code,
            "type": type,
            "extra": extra,
        }


KYCProviderError()


class CBWError(KYCProviderError):
    pass


class PersonaError(KYCProviderError):
    pass


# def format_pydantic_errors(errors: List[dict]) -> List[dict]:
#     formatted_errors = []
#     for error in errors:
#         formatted_error = {}
#         loc_as_tuple = error["loc"]
#         print(error)
#         print(loc_as_tuple)
#         if loc_as_tuple[0] == "body":
#             location = loc_as_tuple[1:]
#         location = ".".join(location)
#         formatted_error[location] = error["msg"]
#         formatted_errors.append(formatted_error)
#     return formatted_errors


def format_pydantic_errors(errors: List[dict]) -> dict:
    formatted_errors = {}
    for error in errors:
        loc_as_tuple = error["loc"]
        if loc_as_tuple[0] == "body":
            location = loc_as_tuple[1:]
        location = ".".join(location)
        formatted_errors[location] = error["msg"]
    return formatted_errors


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        {
            "errors": str(exc),
            "status": 500,
            "code": "generic_exception",
            "type": "server error",
        },
        status_code=500,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        {
            "errors": exc.detail,
            "status": exc.status_code,
            "code": "create_kyc_schema",
            "type": "request error",
        },
        status_code=exc.status_code,
    )


async def validation_exception_handler(
    request: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:

    errors = format_pydantic_errors(exc.errors())
    return JSONResponse(
        {
            # "errors": exc.errors(),
            "errors": errors,
            "status": 400,
            "code": "create_kyc_schema",
            "type": "request error",
        },
        status_code=400,
    )


async def kyc_provider_exception_handler(
    request: Request, exc: Union[CBWError, PersonaError]
) -> JSONResponse:
    return JSONResponse(
        {
            "errors": exc.message,
            "status": exc.status,
            "code": exc.code,
            "type": exc.type,
        },
        status_code=exc.status,
    )