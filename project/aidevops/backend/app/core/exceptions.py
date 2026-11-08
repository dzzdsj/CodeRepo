import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.response import error_json

logger = logging.getLogger(__name__)


class BizException(Exception):
    """业务异常，由全局处理器转换为统一响应体。"""

    def __init__(self, msg: str, code: int = 1000, http_status: int = 400):
        self.msg = msg
        self.code = code
        self.http_status = http_status
        super().__init__(msg)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BizException)
    async def _biz_handler(_: Request, exc: BizException):
        logger.warning("业务异常: code=%s msg=%s", exc.code, exc.msg)
        return error_json(exc.msg, code=exc.code, http_status=exc.http_status)

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(_: Request, exc: RequestValidationError):
        return error_json(f"参数校验失败: {exc.errors()}", code=1001, http_status=422)

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(_: Request, exc: StarletteHTTPException):
        return error_json(str(exc.detail), code=exc.status_code, http_status=exc.status_code)

    @app.exception_handler(Exception)
    async def _unhandled_handler(_: Request, exc: Exception):
        logger.exception("未处理异常: %s", exc)
        msg = str(exc) if settings.debug else "服务器内部错误"
        return error_json(msg, code=5000, http_status=500)
