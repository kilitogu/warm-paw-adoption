"""
领养申请与收藏业务逻辑
作用: 校验申请资格、写入申请单、处理收藏的添加与取消、查询我的收藏与我的申请
"""
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.models.adoption import AdoptionApplication, Favorite
from app.models.pet import Pet
from app.models.user import User
from app.schemas.adoption import (
    AdoptionApplicationResponse,
    AdoptionApplyRequest,
    FavoriteListResponse,
    FavoriteStatusResponse,
)
from app.schemas.pet import PetResponse

# 同一用户最多同时存在的待审核申请数
MAX_PENDING_APPLICATIONS: int = 3


def _to_application_response(
    application: AdoptionApplication, pet_name: str | None = None
) -> AdoptionApplicationResponse:
    """把 ORM 对象转换成带宠物名称的响应结构"""
    return AdoptionApplicationResponse(
        id=application.id,
        user_id=application.user_id,
        pet_id=application.pet_id,
        pet_name=pet_name,
        reason=application.reason,
        status=application.status,
        create_time=application.create_time,
    )


def apply_adoption(
    db: Session, user: User, data: AdoptionApplyRequest
) -> AdoptionApplicationResponse:
    """提交领养申请"""
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if pet is None:
        raise BusinessException(message="宠物不存在或已下架", code=404)

    if pet.status != "可领养":
        raise BusinessException(message="该宠物当前不可申请领养")

    # 同一只宠物不允许重复申请（待审核或已通过都算重复）
    duplicated = (
        db.query(AdoptionApplication)
        .filter(
            AdoptionApplication.user_id == user.id,
            AdoptionApplication.pet_id == data.pet_id,
            AdoptionApplication.status.in_(["待审核", "通过"]),
        )
        .first()
    )
    if duplicated:
        raise BusinessException(message="你已经申请过这只宠物，请耐心等待审核")

    pending_count: int = (
        db.query(AdoptionApplication)
        .filter(
            AdoptionApplication.user_id == user.id,
            AdoptionApplication.status == "待审核",
        )
        .count()
    )
    if pending_count >= MAX_PENDING_APPLICATIONS:
        raise BusinessException(
            message=f"最多同时保留 {MAX_PENDING_APPLICATIONS} 条待审核申请，请等待审核结果"
        )

    application = AdoptionApplication(
        user_id=user.id,
        pet_id=data.pet_id,
        reason=data.reason.strip(),
        status="待审核",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return _to_application_response(application, pet.name)


def toggle_favorite(db: Session, user: User, pet_id: int) -> FavoriteStatusResponse:
    """收藏 / 取消收藏，返回最新状态与收藏总数"""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if pet is None:
        raise BusinessException(message="宠物不存在或已下架", code=404)

    favorite = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.pet_id == pet_id)
        .first()
    )

    if favorite is not None:
        db.delete(favorite)
        db.commit()
        is_favorited: bool = False
    else:
        db.add(Favorite(user_id=user.id, pet_id=pet_id))
        db.commit()
        is_favorited = True

    favorite_count: int = (
        db.query(Favorite).filter(Favorite.pet_id == pet_id).count()
    )

    return FavoriteStatusResponse(
        pet_id=pet_id,
        is_favorited=is_favorited,
        favorite_count=favorite_count,
    )


def get_favorite_status(db: Session, user: User, pet_id: int) -> FavoriteStatusResponse:
    """查询当前用户对某只宠物的收藏状态"""
    is_favorited: bool = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.pet_id == pet_id)
        .first()
        is not None
    )
    favorite_count: int = (
        db.query(Favorite).filter(Favorite.pet_id == pet_id).count()
    )
    return FavoriteStatusResponse(
        pet_id=pet_id,
        is_favorited=is_favorited,
        favorite_count=favorite_count,
    )


def get_favorite_list(
    db: Session, user: User, page: int = 1, page_size: int = 12
) -> FavoriteListResponse:
    """我的收藏：按收藏时间倒序，返回宠物卡片数据"""
    base = (
        db.query(Pet)
        .join(Favorite, Favorite.pet_id == Pet.id)
        .filter(Favorite.user_id == user.id)
    )
    total: int = base.count()
    pets = (
        base.order_by(Favorite.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return FavoriteListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[PetResponse.model_validate(pet) for pet in pets],
    )


def get_my_applications(db: Session, user: User) -> list[AdoptionApplicationResponse]:
    """我的申请：按提交时间倒序"""
    rows = (
        db.query(AdoptionApplication, Pet.name)
        .join(Pet, Pet.id == AdoptionApplication.pet_id)
        .filter(AdoptionApplication.user_id == user.id)
        .order_by(AdoptionApplication.create_time.desc())
        .all()
    )

    return [
        _to_application_response(application, pet_name)
        for application, pet_name in rows
    ]