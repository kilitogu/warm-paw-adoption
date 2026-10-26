"""
领养申请与收藏接口
作用: 申请领养、收藏/取消收藏、查询收藏状态、我的收藏、我的申请
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import Response
from app.dependencies.deps import get_current_user
from app.models.user import User
from app.schemas.adoption import AdoptionApplyRequest, FavoriteRequest
from app.services import adoption_service

router = APIRouter(prefix="/api/adoption", tags=["领养申请"])


@router.post("/apply")
def apply_adoption(
    data: AdoptionApplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交领养申请（必须登录）"""
    result = adoption_service.apply_adoption(db, current_user, data)
    return Response.success(message="申请提交成功，请等待志愿者联系", data=result)


@router.post("/favorite")
def toggle_favorite(
    data: FavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """收藏 / 取消收藏（必须登录）"""
    result = adoption_service.toggle_favorite(db, current_user, data.pet_id)
    message: str = "收藏成功" if result.is_favorited else "已取消收藏"
    return Response.success(message=message, data=result)


@router.get("/favorite/status/{pet_id}")
def get_favorite_status(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询当前用户对某只宠物的收藏状态"""
    result = adoption_service.get_favorite_status(db, current_user, pet_id)
    return Response.success(data=result)


@router.get("/favorite/list")
def get_favorite_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的收藏列表"""
    result = adoption_service.get_favorite_list(
        db, current_user, page=page, page_size=page_size
    )
    return Response.success(data=result)


@router.get("/apply/my")
def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的领养申请列表"""
    result = adoption_service.get_my_applications(db, current_user)
    return Response.success(data=result)