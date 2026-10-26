"""
领养申请与收藏模型
作用:
1. AdoptionApplication 记录用户对某只宠物的领养申请及审核状态
2. Favorite 记录用户收藏的宠物，用于"我的收藏"页面
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AdoptionApplication(Base):

    __tablename__ = "adoption_applications"
    __table_args__ = {"comment": "领养申请表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键ID", sort_order=-1)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="申请用户ID", nullable=False, index=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"), comment="宠物ID", nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, comment="申请理由", nullable=False)
    status: Mapped[str] = mapped_column(String(20), comment="状态：待审核/通过/拒绝", default="待审核", index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间", sort_order=1)
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", sort_order=2)


class Favorite(Base):

    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "pet_id", name="uk_user_pet"),
        {"comment": "宠物收藏表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键ID", sort_order=-1)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), comment="用户ID", nullable=False, index=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id"), comment="宠物ID", nullable=False, index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="收藏时间", sort_order=1)