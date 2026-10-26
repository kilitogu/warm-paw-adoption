"""
数据库连接配置
作用: 创建数据库引擎和会话工厂
相当于整个系统的数据源
创建全局Base类
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


# 1. 定义 Base（全局唯一）
class Base(DeclarativeBase):
    pass

# 创建数据库引擎
# pool_pre_ping=True: 每次使用连接前先测试连通性, 避免连接断开后报错
# pool_recycle=3600: 连接的回收时间(秒), 每隔1个小时回收一次连接
# echo=False: 不在控制台打印sql语句(调试的时候可以改为True)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# 创建会话工厂
# autocommit=False: 不自动提交, 需要手动提交(数据更安全)
# autoflush=False: 不自动刷新, 查询前不会自动把内存中的修改同步到数据库
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    数据库会话依赖
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()