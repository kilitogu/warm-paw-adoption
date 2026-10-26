"""
宠物信息模型
作用: 保存待领养宠物的基础信息、健康信息与展示图片
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Pet(Base):

    __tablename__ = "pets"
    __table_args__ = {"comment": "宠物信息表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键ID", sort_order=-1)
    name: Mapped[str] = mapped_column(String(50), comment="宠物昵称", nullable=False)
    species: Mapped[str] = mapped_column(String(20), comment="物种：猫/狗/其他", nullable=False, index=True)
    breed: Mapped[str | None] = mapped_column(String(50), comment="品种")
    gender: Mapped[str] = mapped_column(String(10), comment="性别：公/母", default="公")
    age_months: Mapped[int] = mapped_column(Integer, comment="月龄", default=0)
    city: Mapped[str | None] = mapped_column(String(50), comment="所在城市", index=True)
    health_status: Mapped[str] = mapped_column(String(20), comment="健康状况：健康/亚健康/需治疗", default="健康")
    vaccinated: Mapped[bool] = mapped_column(Boolean, comment="是否已接种疫苗", default=False)
    sterilized: Mapped[bool] = mapped_column(Boolean, comment="是否已绝育", default=False)
    description: Mapped[str | None] = mapped_column(Text, comment="宠物介绍")
    cover_image: Mapped[str | None] = mapped_column(String(255), comment="封面图地址")
    images: Mapped[list | None] = mapped_column(JSON, comment="相册图片列表")
    status: Mapped[str] = mapped_column(String(20), comment="状态：可领养/审核中/已领养", default="可领养", index=True)
    view_count: Mapped[int] = mapped_column(Integer, comment="浏览量", default=0)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间", sort_order=1)
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", sort_order=2)

    @property
    def age_text(self) -> str:
        """把月龄转换成前端可直接展示的中文年龄"""
        months: int = int(self.age_months or 0)
        if months <= 0:
            return "不满1个月"
        if months < 12:
            return f"{months}个月"
        year: int = months // 12
        rest: int = months % 12
        return f"{year}岁" if rest == 0 else f"{year}岁{rest}个月"