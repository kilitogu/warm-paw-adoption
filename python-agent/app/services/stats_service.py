"""
平台数据统计
作用: 为首页数据看板提供在架宠物数、累计领养数、合作救助站数
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.pet import Pet

# 合作救助站暂未建表，先用常量占位；后续新增 organizations 表后替换为数据库统计
ORG_TOTAL: int = 36


def get_overview(db: Session) -> dict:
    """首页数据看板"""
    pet_total: int = (
        db.query(func.count(Pet.id)).filter(Pet.status == "可领养").scalar() or 0
    )
    adopted_total: int = (
        db.query(func.count(Pet.id)).filter(Pet.status == "已领养").scalar() or 0
    )

    return {
        "pet_total": int(pet_total),
        "adopted_total": int(adopted_total),
        "org_total": ORG_TOTAL,
    }