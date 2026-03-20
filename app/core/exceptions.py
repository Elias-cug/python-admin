from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class BusinessError(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


class NotFoundError(BusinessError):
    def __init__(self, message: str = "resource not found", code=400):
        super().__init__(message, 404)


class PermissionError(BusinessError):
    def __init__(self, message="permission denied", code=400):
        super().__init__(message, 403)


async def business_expection_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


async def global_exception_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "internal server error", "data": None},
    )


def register_exception(app: FastAPI):
    app.add_exception_handler(BusinessError, business_expection_handler)
    app.add_exception_handler(Exception, global_exception_handler)
