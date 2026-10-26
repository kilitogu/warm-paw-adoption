"""
领养指南相关的响应模型
作用: 约束 FAQ 接口返回的字段结构
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GuideFaqResponse(BaseModel):
    """单条 FAQ"""

    id: int
    category: str
    question: str
    answer: str
    sort_order: int = 0
    create_time: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GuideFaqGroupResponse(BaseModel):
    """按分类聚合后的 FAQ"""

    category: str
    items: list[GuideFaqResponse]