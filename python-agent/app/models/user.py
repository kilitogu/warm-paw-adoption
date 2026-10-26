from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime

from app.core.database import Base


class User(Base):

    __tablename__ = "users"
    __table_args__ = {"comment": "用户信息表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键ID", sort_order=-1)
    username: Mapped[str] = mapped_column(String(50), comment="账号", nullable=False)
    password: Mapped[str] = mapped_column(String(200), comment="密码", nullable=False)
    name: Mapped[str] = mapped_column(String(50), comment="名称", nullable=False)
    role: Mapped[str] = mapped_column(String(50), comment="角色：user-用户，admin-管理员", nullable=False)
    email: Mapped[str | None] = mapped_column(String(50), comment="邮箱")
    phone: Mapped[str | None] = mapped_column(String(50), comment="手机号")
    avatar: Mapped[str | None] = mapped_column(String(50), comment="头像")
    status: Mapped[int] = mapped_column(default=1, comment="状态：0-禁用，1-正常")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间", sort_order=1)
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", sort_order=2)
