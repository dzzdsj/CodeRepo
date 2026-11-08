from typing import Any

from fastapi.responses import JSONResponse


def success(data: Any = None, msg: str = "ok") -> dict[str, Any]:
    """统一成功响应体。"""
    return {"code": 0, "msg": msg, "data": data}


def error_json(
    msg: str, code: int = 1000, http_status: int = 400
) -> JSONResponse:
    """统一错误响应体。"""
    return JSONResponse(
        status_code=http_status,
        content={"code": code, "msg": msg, "data": None},
    )
