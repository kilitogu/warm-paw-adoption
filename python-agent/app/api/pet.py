"""
宠物相关接口
作用: 提供宠物列表、宠物详情、首页推荐三个查询接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import Response
from app.schemas.pet import PetQueryRequest
from app.services import pet_service

router = APIRouter(prefix="/api/pet", tags=["宠物信息"])


@router.get("/list")
def get_pet_list(query: PetQueryRequest = Depends(), db: Session = Depends(get_db)):
    """宠物列表：分页 + 多条件筛选 + 排序"""
    data = pet_service.get_pet_list(db, query)
    return Response.success(data=data)


# 注意：/recommend 必须写在 /{pet_id} 之前，否则会被当成 pet_id 解析
@router.get("/recommend")
def get_recommend_pets(limit: int = 6, db: Session = Depends(get_db)):
    """首页精选宠物"""
    data = pet_service.get_recommend_pets(db, limit=limit)
    return Response.success(data=data)


@router.get("/{pet_id}")
def get_pet_detail(pet_id: int, db: Session = Depends(get_db)):
    """宠物详情"""
    data = pet_service.get_pet_detail(db, pet_id)
    return Response.success(data=data)