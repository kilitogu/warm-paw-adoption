from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.exceptions import BusinessException
from app.core.response import Response


async def business_exception_handler(request: Request, exc: BusinessException):
    """处理业务异常（主动抛出）"""
    logger.warning(f"业务异常: {exc.message} | 路径: {request.url.path}")
    return JSONResponse(
        status_code=200,  # 按照你们规范，业务错误通常返回 HTTP 200
        content=Response.error(code=exc.code, message=exc.message).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTP 异常（比如 401 未授权，404 找不到）"""
    logger.warning(f"HTTP异常: {exc.detail} | 路径: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content=Response.error(code=exc.status_code, message=exc.detail).model_dump(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理参数校验异常（422）"""
    # 提取具体的字段错误，给前端更友好的提示
    errors = exc.errors()
    first_error = errors[0]
    field = first_error.get("loc", [])[-1]
    msg = first_error.get("msg", "参数错误")
    friendly_msg = f"参数 [{field}] 校验失败: {msg}"

    logger.warning(f"参数校验异常: {friendly_msg} | 路径: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content=Response.error(code=422, message=friendly_msg).model_dump(),
    )


async def global_exception_handler(request: Request, exc: Exception):
    """兜底全局异常处理器（500）"""
    # 这里必须用 logger.exception，它会打印完整的报错堆栈，方便开发排查
    logger.exception(f"系统内部错误: {str(exc)} | 路径: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content=Response.error(code=500, message="服务器内部错误，请联系管理员").model_dump(),
    )


def register_exception_handlers(app: FastAPI):
    """统一注册所有异常处理器"""
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)