"""
模型统一导出
作用: 方便外部一次性导入所有模型，或者触发建表时的模型注册
"""
from app.models.adoption import AdoptionApplication, Favorite
from app.models.guide import GuideFaq
from app.models.pet import Pet
from app.models.user import User

__all__ = ["User", "Pet", "AdoptionApplication", "Favorite", "GuideFaq"]