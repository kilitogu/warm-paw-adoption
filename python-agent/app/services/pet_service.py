"""
宠物业务逻辑
作用: 封装宠物列表筛选、详情查询、首页推荐，API 层只负责接收参数和返回 Response
"""
from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.core.exceptions import BusinessException
from app.models.pet import Pet
from app.schemas.pet import PetListResponse, PetQueryRequest, PetResponse


def _build_pet_query(db: Session, query: PetQueryRequest) -> Query:
    """根据筛选条件拼装查询对象"""
    q: Query = db.query(Pet)

    # 状态筛选：默认只看可领养的宠物
    if query.status:
        q = q.filter(Pet.status == query.status)

    if query.species:
        q = q.filter(Pet.species == query.species)

    if query.breed:
        q = q.filter(Pet.breed == query.breed)

    if query.gender:
        q = q.filter(Pet.gender == query.gender)

    if query.city:
        q = q.filter(Pet.city == query.city)

    if query.age_min is not None:
        q = q.filter(Pet.age_months >= query.age_min)

    if query.age_max is not None:
        q = q.filter(Pet.age_months <= query.age_max)

    if query.health_status:
        q = q.filter(Pet.health_status == query.health_status)

    if query.vaccinated is not None:
        q = q.filter(Pet.vaccinated == query.vaccinated)

    if query.sterilized is not None:
        q = q.filter(Pet.sterilized == query.sterilized)

    if query.keyword:
        keyword: str = f"%{query.keyword.strip()}%"
        q = q.filter(
            or_(
                Pet.name.like(keyword),
                Pet.breed.like(keyword),
                Pet.description.like(keyword),
            )
        )

    return q


def _apply_sort(q: Query, sort_by: str) -> Query:
    """统一处理排序规则"""
    if sort_by == "hot":
        return q.order_by(Pet.view_count.desc(), Pet.create_time.desc())
    if sort_by == "age":
        return q.order_by(Pet.age_months.asc(), Pet.create_time.desc())
    # 默认最新
    return q.order_by(Pet.create_time.desc())


def get_pet_list(db: Session, query: PetQueryRequest) -> PetListResponse:
    """宠物列表：分页 + 多条件筛选 + 排序"""
    q: Query = _build_pet_query(db, query)
    total: int = q.count()

    items = (
        _apply_sort(q, query.sort_by)
        .offset((query.page - 1) * query.page_size)
        .limit(query.page_size)
        .all()
    )

    return PetListResponse(
        total=total,
        page=query.page,
        page_size=query.page_size,
        items=[PetResponse.model_validate(item) for item in items],
    )


def get_pet_detail(db: Session, pet_id: int) -> PetResponse:
    """宠物详情：不存在时抛业务异常，存在时浏览量 +1"""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if pet is None:
        raise BusinessException(message="宠物不存在或已下架", code=404)

    pet.view_count = int(pet.view_count or 0) + 1
    db.commit()
    db.refresh(pet)

    return PetResponse.model_validate(pet)


def get_recommend_pets(db: Session, limit: int = 6) -> list[PetResponse]:
    """首页精选：取可领养宠物中浏览量最高的若干只"""
    pets = (
        db.query(Pet)
        .filter(Pet.status == "可领养")
        .order_by(Pet.view_count.desc(), Pet.create_time.desc())
        .limit(limit)
        .all()
    )
    return [PetResponse.model_validate(pet) for pet in pets]