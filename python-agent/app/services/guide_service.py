"""
领养指南业务逻辑
作用: 查询 FAQ，并按分类聚合，方便前端折叠面板分组展示
"""
from sqlalchemy.orm import Session

from app.models.guide import GuideFaq
from app.schemas.guide import GuideFaqGroupResponse, GuideFaqResponse


def get_faq_list(db: Session, category: str | None = None) -> list[GuideFaqResponse]:
    """查询所有启用的 FAQ，可按分类过滤"""
    query = db.query(GuideFaq).filter(GuideFaq.status == 1)

    if category:
        query = query.filter(GuideFaq.category == category)

    rows = query.order_by(GuideFaq.sort_order.asc(), GuideFaq.id.asc()).all()
    return [GuideFaqResponse.model_validate(row) for row in rows]


def get_faq_groups(db: Session) -> list[GuideFaqGroupResponse]:
    """按分类聚合 FAQ，保持数据库中的排序"""
    faqs = get_faq_list(db)
    groups: dict[str, list[GuideFaqResponse]] = {}

    for faq in faqs:
        groups.setdefault(faq.category, []).append(faq)

    return [
        GuideFaqGroupResponse(category=category, items=items)
        for category, items in groups.items()
    ]