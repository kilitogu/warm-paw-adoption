"""
宠物相关的请求/响应模型
作用: 约束接口入参，并统一返回给前端的字段结构
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class PetQueryRequest(BaseModel):
    """宠物列表查询参数"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=12, ge=1, le=50, description="每页条数")
    species: str | None = Field(default=None, description="物种：猫/狗/其他")
    breed: str | None = Field(default=None, description="品种")
    gender: str | None = Field(default=None, description="性别：公/母")
    city: str | None = Field(default=None, description="城市")
    age_min: int | None = Field(default=None, ge=0, description="最小月龄")
    age_max: int | None = Field(default=None, ge=0, description="最大月龄")
    health_status: str | None = Field(default=None, description="健康状况")
    vaccinated: bool | None = Field(default=None, description="是否已接种疫苗")
    sterilized: bool | None = Field(default=None, description="是否已绝育")
    keyword: str | None = Field(default=None, description="昵称/品种/描述关键词")
    status: str | None = Field(default="可领养", description="宠物状态")
    sort_by: Literal["latest", "hot", "age"] = Field(default="latest", description="排序：latest-最新，hot-最热，age-年龄")


class PetResponse(BaseModel):
    """宠物列表/详情返回结构"""

    id: int
    name: str
    species: str
    breed: str | None = None
    gender: str
    age_months: int
    city: str | None = None
    health_status: str
    vaccinated: bool
    sterilized: bool
    description: str | None = None
    cover_image: str | None = None
    images: list[str] | None = None
    status: str
    view_count: int = 0
    create_time: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field(description="年龄中文描述")
    @property
    def age_text(self) -> str:
        """根据月龄生成中文年龄，前端无需重复计算"""
        months: int = int(self.age_months or 0)
        if months <= 0:
            return "不满1个月"
        if months < 12:
            return f"{months}个月"
        year: int = months // 12
        rest: int = months % 12
        return f"{year}岁" if rest == 0 else f"{year}岁{rest}个月"


class PetListResponse(BaseModel):
    """宠物分页列表返回结构"""

    total: int
    page: int
    page_size: int
    items: list[PetResponse]