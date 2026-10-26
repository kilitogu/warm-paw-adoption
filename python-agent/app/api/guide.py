"""
领养指南接口
作用: 提供 FAQ 列表与分类聚合数据
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import Response
from app.services import guide_service

router = APIRouter(prefix="/api/guide", tags=["领养指南"])


@router.get("/faq")
def get_faq_list(
    category: str | None = Query(default=None, description="分类，不传则返回全部"),
    db: Session = Depends(get_db),
):
    """FAQ 列表（结构化字段：id/category/question/answer）"""
    data = guide_service.get_faq_list(db, category=category)
    return Response.success(data=data)


@router.get("/faq/groups")
def get_faq_groups(db: Session = Depends(get_db)):
    """按分类聚合的 FAQ，供折叠面板分组展示"""
    data = guide_service.get_faq_groups(db)
    return Response.success(data=data)