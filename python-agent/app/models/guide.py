"""
领养指南 FAQ 模型
作用: 保存领养条件、流程、材料、健康与责任告知等常见问题
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GuideFaq(Base):

    __tablename__ = "guide_faqs"
    __table_args__ = {"comment": "领养指南FAQ表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键ID", sort_order=-1)
    category: Mapped[str] = mapped_column(String(50), comment="分类：领养条件/申请流程/宠物健康/领养后", nullable=False, index=True)
    question: Mapped[str] = mapped_column(String(200), comment="问题", nullable=False)
    answer: Mapped[str] = mapped_column(Text, comment="回答", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, comment="排序值，越小越靠前", default=0, sort_order=0)
    status: Mapped[int] = mapped_column(Integer, comment="状态：0-隐藏，1-显示", default=1)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间", sort_order=1)
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", sort_order=2)