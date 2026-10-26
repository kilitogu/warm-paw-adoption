"""
领养申请与收藏相关的请求/响应模型
作用: 申请领养、收藏宠物、我的收藏、我的申请等接口的数据约束
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pet import PetResponse


class AdoptionApplyRequest(BaseModel):
    """提交领养申请"""

    pet_id: int = Field(gt=0, description="宠物ID")
    reason: str = Field(min_length=10, max_length=500, description="申请理由，至少10个字")


class AdoptionApplicationResponse(BaseModel):
    """领养申请返回结构"""

    id: int
    user_id: int
    pet_id: int
    pet_name: str | None = None
    reason: str
    status: str
    create_time: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class FavoriteRequest(BaseModel):
    """收藏/取消收藏"""

    pet_id: int = Field(gt=0, description="宠物ID")


class FavoriteStatusResponse(BaseModel):
    """当前用户对某只宠物的收藏状态"""

    pet_id: int
    is_favorited: bool
    favorite_count: int


class FavoriteListResponse(BaseModel):
    """我的收藏列表"""

    total: int
    page: int
    page_size: int
    items: list[PetResponse]