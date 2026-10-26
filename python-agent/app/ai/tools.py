"""
AI Tool Calling 工具集
作用:
1. 用 Pydantic 定义每个工具的入参 Schema，约束 LLM 生成的参数
2. 用 functools.partial 注入 db 与 auth_user_id，避免把数据库会话暴露给模型
3. 统一捕获异常，返回结构化结果，不把底层异常抛给 LangGraph
"""
from functools import partial
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.adoption import AdoptionApplication, Favorite
from app.models.pet import Pet
from app.models.user import User

# 同时待审核申请上限，与 adoption_service 保持一致
MAX_PENDING_APPLICATIONS: int = 3

# SSE 层用于识别工具事件的工具名集合
TOOL_NAMES: set[str] = {
    "search_pets",
    "get_pet_detail",
    "check_adoption_eligibility",
    "submit_adoption_intent",
    "get_platform_stats",
}


# =========================================================
# 入参 Schema
# =========================================================
class SearchPetsInput(BaseModel):
    """按条件搜索宠物"""

    species: str | None = Field(default=None, description="物种，只能是：猫、狗、其他")
    breed: str | None = Field(default=None, description="品种，例如布偶猫、柯基")
    city: str | None = Field(default=None, description="城市，例如杭州、上海")
    age_min: int | None = Field(default=None, ge=0, le=300, description="最小月龄")
    age_max: int | None = Field(default=None, ge=0, le=300, description="最大月龄")
    gender: str | None = Field(default=None, description="性别：公或母")


class GetPetDetailInput(BaseModel):
    """查询单只宠物详情"""

    pet_id: int = Field(gt=0, description="宠物ID，必须来自搜索结果")


class CheckEligibilityInput(BaseModel):
    """领养资格校验"""

    user_id: int = Field(gt=0, description="当前登录用户ID")


class SubmitAdoptionIntentInput(BaseModel):
    """提交领养申请（不包含 confirmed 字段，防止模型绕过确认）"""

    user_id: int = Field(gt=0, description="当前登录用户ID")
    pet_id: int = Field(gt=0, description="要申请的宠物ID")
    reason: str = Field(min_length=10, max_length=500, description="申请理由，至少10个字")


class PlatformStatsInput(BaseModel):
    """平台统计工具无入参"""


# =========================================================
# 通用返回结构
# =========================================================
def _ok(**payload: Any) -> dict:
    """工具执行成功"""
    return {"ok": True, **payload}


def _err(message: str, code: str = "tool_error") -> dict:
    """工具执行失败，返回结构化错误，由 LLM 转述给用户"""
    return {"ok": False, "code": code, "error": message}


def _pet_brief(pet: Pet) -> dict:
    """列表场景的精简字段，减少 token 消耗"""
    return {
        "id": pet.id,
        "name": pet.name,
        "species": pet.species,
        "breed": pet.breed,
        "gender": pet.gender,
        "age_months": pet.age_months,
        "age_text": pet.age_text,
        "city": pet.city,
        "status": pet.status,
        "cover_image": pet.cover_image,
    }


def _pet_detail(pet: Pet, favorite_count: int = 0) -> dict:
    """详情场景的完整字段"""
    return {
        **_pet_brief(pet),
        "health_status": pet.health_status,
        "vaccinated": bool(pet.vaccinated),
        "sterilized": bool(pet.sterilized),
        "description": pet.description,
        "images": pet.images or [],
        "view_count": pet.view_count,
        "favorite_count": favorite_count,
    }


# =========================================================
# 工具实现
# =========================================================
def search_pets(
    db: Session,
    species: str | None = None,
    breed: str | None = None,
    city: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    gender: str | None = None,
) -> dict:
    """按条件查询可领养宠物，最多返回 5 条"""
    try:
        query = db.query(Pet).filter(Pet.status == "可领养")

        if species:
            query = query.filter(Pet.species == species)
        if breed:
            query = query.filter(Pet.breed.like(f"%{breed}%"))
        if city:
            query = query.filter(Pet.city == city)
        if gender:
            query = query.filter(Pet.gender == gender)
        if age_min is not None:
            query = query.filter(Pet.age_months >= age_min)
        if age_max is not None:
            query = query.filter(Pet.age_months <= age_max)

        total: int = query.count()
        pets = query.order_by(Pet.view_count.desc()).limit(5).all()

        logger.info(
            f"工具 search_pets | species={species} breed={breed} city={city} "
            f"age={age_min}-{age_max} gender={gender} | 命中={total}"
        )

        return _ok(
            total=total,
            count=len(pets),
            items=[_pet_brief(pet) for pet in pets],
            message=f"找到 {total} 只符合条件的宠物" if total else "没有找到符合条件的宠物",
        )
    except Exception:
        logger.exception("工具 search_pets 执行失败")
        return _err("查询宠物失败，请稍后重试")


def get_pet_detail(db: Session, pet_id: int) -> dict:
    """查询单只宠物完整信息"""
    try:
        pet = db.query(Pet).filter(Pet.id == pet_id).first()
        if pet is None:
            return _err("宠物不存在或已下架", code="pet_not_found")

        favorite_count: int = (
            db.query(Favorite).filter(Favorite.pet_id == pet_id).count()
        )

        logger.info(f"工具 get_pet_detail | pet_id={pet_id} | 名称={pet.name}")

        return _ok(pet=_pet_detail(pet, favorite_count))
    except Exception:
        logger.exception("工具 get_pet_detail 执行失败")
        return _err("查询宠物详情失败，请稍后重试")


def check_adoption_eligibility(db: Session, user_id: int) -> dict:
    """校验用户是否满足领养申请条件"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return _err("用户不存在，请重新登录", code="user_not_found")

        missing: list[str] = []

        if int(user.status) != 1:
            missing.append("账号状态异常，请联系管理员")

        pending_count: int = (
            db.query(AdoptionApplication)
            .filter(
                AdoptionApplication.user_id == user_id,
                AdoptionApplication.status == "待审核",
            )
            .count()
        )

        if pending_count >= MAX_PENDING_APPLICATIONS:
            missing.append(
                f"待审核申请已达 {MAX_PENDING_APPLICATIONS} 条，请等待审核结果"
            )

        # 手机号不阻断申请，只作为提醒，避免新注册用户无法体验 AI 申请
        contact_ready: bool = bool(user.phone)

        logger.info(
            f"工具 check_adoption_eligibility | user_id={user_id} | "
            f"eligible={not missing} | missing={missing}"
        )

        return _ok(
            user_id=user_id,
            eligible=not missing,
            missing=missing,
            pending_count=pending_count,
            max_pending=MAX_PENDING_APPLICATIONS,
            contact_ready=contact_ready,
            hint="" if contact_ready else "建议在账号设置补充手机号，方便志愿者联系你",
        )
    except Exception:
        logger.exception("工具 check_adoption_eligibility 执行失败")
        return _err("资格校验失败，请稍后重试")


def submit_adoption_intent(
    db: Session,
    user_id: int,
    pet_id: int,
    reason: str,
    auth_user_id: int | None = None,
    confirmed: bool = False,
) -> dict:
    """
    提交领养申请

    confirmed=False 时只返回二次确认指令，不写数据库
    auth_user_id 由 partial 注入，用于防止模型伪造 user_id
    """
    try:
        # 1. 权限校验：入参 user_id 必须与 token 中的用户一致
        if auth_user_id is not None and int(user_id) != int(auth_user_id):
            logger.warning(
                f"工具 submit_adoption_intent 越权拦截 | 入参={user_id} token={auth_user_id}"
            )
            return _err("无权以其他用户身份提交申请", code="forbidden")

        # 2. 账号状态校验，避免 LLM 绕过资格检查直接提交
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return _err("用户不存在，请重新登录", code="user_not_found")
        if int(user.status) != 1:
            return _err("账号状态异常，暂时无法提交申请", code="user_disabled")

        # 3. 基础校验
        pet = db.query(Pet).filter(Pet.id == pet_id).first()
        if pet is None:
            return _err("宠物不存在或已下架", code="pet_not_found")

        if pet.status != "可领养":
            return _err(f"{pet.name} 当前状态为「{pet.status}」，暂不可申请")

        if len(reason.strip()) < 10:
            return _err("申请理由至少需要 10 个字", code="invalid_reason")

        # 4. 二次确认：未确认时只返回确认指令
        if not confirmed:
            logger.info(
                f"工具 submit_adoption_intent 等待确认 | user_id={user_id} pet_id={pet_id}"
            )
            return {
                "ok": False,
                "need_confirm": True,
                "action": "submit_adoption",
                "pet_id": pet.id,
                "pet_name": pet.name,
                "reason": reason.strip(),
                "message": f"即将为「{pet.name}」提交领养申请，请确认后我再提交。",
            }

        # 5. 重复申请与数量上限
        duplicated = (
            db.query(AdoptionApplication)
            .filter(
                AdoptionApplication.user_id == user_id,
                AdoptionApplication.pet_id == pet_id,
                AdoptionApplication.status.in_(["待审核", "通过"]),
            )
            .first()
        )
        if duplicated:
            return _err("你已经申请过这只宠物，请耐心等待审核", code="duplicated")

        pending_count: int = (
            db.query(AdoptionApplication)
            .filter(
                AdoptionApplication.user_id == user_id,
                AdoptionApplication.status == "待审核",
            )
            .count()
        )
        if pending_count >= MAX_PENDING_APPLICATIONS:
            return _err(
                f"待审核申请已达 {MAX_PENDING_APPLICATIONS} 条，暂时无法提交",
                code="limit_reached",
            )

        # 6. 真正写库
        application = AdoptionApplication(
            user_id=user_id,
            pet_id=pet_id,
            reason=reason.strip(),
            status="待审核",
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        logger.info(
            f"工具 submit_adoption_intent 提交成功 | application_id={application.id} "
            f"user_id={user_id} pet_id={pet_id}"
        )

        return _ok(
            application_id=application.id,
            pet_id=pet_id,
            pet_name=pet.name,
            status=application.status,
            message=f"已成功提交对「{pet.name}」的领养申请，志愿者会在 48 小时内联系你。",
        )
    except Exception:
        db.rollback()
        logger.exception("工具 submit_adoption_intent 执行失败")
        return _err("提交申请失败，请稍后重试")


def submit_confirmed(db: Session, user_id: int, pet_id: int, reason: str) -> dict:
    """
    用户在前端点击"确认"后由 confirm_apply 节点调用
    与工具分离，确保 LLM 无法直接触发写库
    """
    return submit_adoption_intent(
        db=db,
        user_id=user_id,
        pet_id=pet_id,
        reason=reason,
        auth_user_id=user_id,
        confirmed=True,
    )


def get_platform_stats(db: Session) -> dict:
    """平台数据看板"""
    try:
        pet_total: int = db.query(Pet).filter(Pet.status == "可领养").count()
        adopted_total: int = db.query(Pet).filter(Pet.status == "已领养").count()
        cat_total: int = (
            db.query(Pet)
            .filter(Pet.status == "可领养", Pet.species == "猫")
            .count()
        )
        dog_total: int = (
            db.query(Pet)
            .filter(Pet.status == "可领养", Pet.species == "狗")
            .count()
        )
        pending_applications: int = (
            db.query(AdoptionApplication)
            .filter(AdoptionApplication.status == "待审核")
            .count()
        )

        logger.info("工具 get_platform_stats 执行成功")

        return _ok(
            pet_total=pet_total,
            adopted_total=adopted_total,
            cat_total=cat_total,
            dog_total=dog_total,
            pending_applications=pending_applications,
            # 合作救助站暂未建表，先用常量占位；后续新增 organizations 表后改为数据库统计
            org_total=36,
        )
    except Exception:
        logger.exception("工具 get_platform_stats 执行失败")
        return _err("查询平台数据失败，请稍后重试")


# =========================================================
# 工具构建
# =========================================================
def build_tools(db: Session, user_id: int) -> list[BaseTool]:
    """
    为当前请求构建 5 个工具

    db、auth_user_id、confirmed 通过 partial 注入，LLM 只能看到 args_schema 中的字段
    """
    tools: list[BaseTool] = [
        StructuredTool.from_function(
            func=partial(search_pets, db=db),
            name="search_pets",
            description=(
                "按物种、品种、城市、年龄区间、性别查询可领养宠物，返回精简列表。"
                "当用户想找猫、找狗、问某城市有哪些宠物时调用。"
            ),
            args_schema=SearchPetsInput,
        ),
        StructuredTool.from_function(
            func=partial(get_pet_detail, db=db),
            name="get_pet_detail",
            description=(
                "根据宠物ID查询完整信息，包括健康、疫苗、绝育、描述与收藏数。"
                "当用户询问某一只宠物的具体情况时调用。"
            ),
            args_schema=GetPetDetailInput,
        ),
        StructuredTool.from_function(
            func=partial(check_adoption_eligibility, db=db),
            name="check_adoption_eligibility",
            description=(
                "检查当前登录用户是否满足领养申请条件，返回缺失项。"
                "在用户准备申请领养前调用。"
            ),
            args_schema=CheckEligibilityInput,
        ),
        StructuredTool.from_function(
            func=partial(
                submit_adoption_intent,
                db=db,
                auth_user_id=user_id,
                confirmed=False,
            ),
            name="submit_adoption_intent",
            description=(
                "提交领养申请。调用后不会立即写入数据库，"
                "会返回 need_confirm 让用户确认，确认后由系统完成提交。"
                "只有用户明确说“帮我申请”“提交申请”时才调用。"
            ),
            args_schema=SubmitAdoptionIntentInput,
        ),
        StructuredTool.from_function(
            func=partial(get_platform_stats, db=db),
            name="get_platform_stats",
            description=(
                "查询平台数据看板，包括在架宠物数、累计领养数、猫狗数量、待审核申请数。"
                "当用户问平台有多少只猫、领养了多少只时调用。"
            ),
            args_schema=PlatformStatsInput,
        ),
    ]

    return tools


def build_readonly_tools(db: Session, user_id: int) -> list[BaseTool]:
    """
    第 3 步只绑定只读工具

    提交申请涉及写库与二次确认，留到第 4 步由 LangGraph 的 interrupt 处理
    """
    return [
        tool
        for tool in build_tools(db, user_id)
        if tool.name != "submit_adoption_intent"
    ]


def get_tool_map(tools: list[BaseTool]) -> dict[str, BaseTool]:
    """工具名到工具对象的映射，供工具循环或 tool_call 节点执行"""
    return {tool.name: tool for tool in tools}
