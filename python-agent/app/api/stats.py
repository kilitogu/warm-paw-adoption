"""
平台数据统计接口
作用: 首页数据看板一次性拿到三个核心指标
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import Response
from app.services import stats_service

router = APIRouter(prefix="/api/stats", tags=["平台统计"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    """平台数据看板：在架宠物数 / 累计领养数 / 合作救助站数"""
    data = stats_service.get_overview(db)
    return Response.success(data=data)