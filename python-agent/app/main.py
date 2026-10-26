"""
FastAPI 应用入口
作用: 创建应用、初始化数据库、注册中间件 / 异常处理 / 路由
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

import app.models  # noqa: F401  触发模型注册，create_all 才能建表
from app.api import adoption, ai, file, guide, login, pet, register, stats, user
from app.core.config import UPLOAD_DIR, settings
from app.core.database import Base, engine
from app.core.exception_handlers import register_exception_handlers
from app.core.logger import logger
from app.core.response import Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时打印访问地址，关闭时记录日志"""
    logger.info(
        "\n------------------------------------------\n"
        f"  {settings.app_name} 启动成功!\n"
        f"  接口文档地址: http://localhost:{settings.server_port}/docs\n"
        f"  后端首页地址: http://localhost:{settings.server_port}/\n"
        "------------------------------------------"
    )
    yield
    logger.info("应用正在关闭...")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# 根据已注册的模型创建数据表
# 生产环境建议使用 Alembic 迁移，而不是 create_all
Base.metadata.create_all(bind=engine)

# 注册全局异常处理
register_exception_handlers(app)

# 跨域：allow_credentials=True 时 allow_origins 不能写 ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # 包含 Authorization 与 Content-Type
)

# 注意：不要给 SSE 响应加 GZip / Brotli 压缩中间件
# 压缩中间件会等缓冲区攒满才发送，前端会一次性收到整段文本，看起来像"没有流式输出"

# 挂载静态资源：/uploads/xxx.jpg → uploads/xxx.jpg
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(login.router)
app.include_router(register.router)
app.include_router(user.router)
app.include_router(file.router)
app.include_router(pet.router)
app.include_router(stats.router)
app.include_router(adoption.router)
app.include_router(guide.router)
app.include_router(ai.router)


@app.get("/", tags=["系统"])
def index():
    """后端健康检查与项目信息"""
    return Response.success(
        message="暖爪后端服务运行中",
        data={
            "app": settings.app_name,
            "docs": "/docs",
            "health": "/health",
        },
    )


@app.get("/health", tags=["系统"])
def health():
    """健康检查：供容器探针与部署脚本使用"""
    return {"status": "ok"}
