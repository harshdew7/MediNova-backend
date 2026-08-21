from fastapi import Request
from fastapi.responses import JSONResponse


class MediNovaException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
    ):
        self.message = message
        self.status_code = status_code


async def medinova_exception_handler(
    request: Request,
    exc: MediNovaException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
        },
    )