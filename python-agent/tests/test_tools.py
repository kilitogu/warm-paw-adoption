"""
AI 工具单元测试

运行方式（无需额外依赖）:
    python -m unittest discover -s tests -v

安装了 pytest 时也可以:
    pytest tests/test_tools.py -v
"""
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  注册所有模型
from app.ai import tools as ai_tools
from app.core.database import Base
from app.models.adoption import AdoptionApplication
from app.models.pet import Pet
from app.models.user import User


class ToolTestCase(unittest.TestCase):
    """每个用例使用独立的内存数据库"""

    def setUp(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        self.session = sessionmaker(bind=engine)()

        self.session.add_all(
            [
                User(
                    id=1,
                    username="tester",
                    password="hashed",
                    name="测试用户",
                    role="user",
                    phone="13800138000",
                    email="tester@example.com",
                    status=1,
                ),
                Pet(
                    id=1,
                    name="奶糖",
                    species="猫",
                    breed="布偶猫",
                    gender="母",
                    age_months=8,
                    city="杭州",
                    health_status="健康",
                    vaccinated=True,
                    sterilized=True,
                    description="性格黏人",
                    status="可领养",
                    view_count=10,
                ),
            ]
        )
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()

    def test_search_pets_by_species(self) -> None:
        """按物种搜索应命中 1 条"""
        result = ai_tools.search_pets(self.session, species="猫")

        self.assertTrue(result["ok"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["name"], "奶糖")
        self.assertEqual(result["items"][0]["age_text"], "8个月")

    def test_search_pets_no_match(self) -> None:
        """没有命中时返回空列表与提示"""
        result = ai_tools.search_pets(self.session, city="北京")

        self.assertTrue(result["ok"])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["items"], [])

    def test_get_pet_detail(self) -> None:
        """详情应包含健康与疫苗信息"""
        result = ai_tools.get_pet_detail(self.session, 1)

        self.assertTrue(result["ok"])
        self.assertEqual(result["pet"]["name"], "奶糖")
        self.assertTrue(result["pet"]["vaccinated"])
        self.assertEqual(result["pet"]["favorite_count"], 0)

    def test_get_pet_detail_not_found(self) -> None:
        """不存在的宠物返回结构化错误"""
        result = ai_tools.get_pet_detail(self.session, 999)

        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "pet_not_found")

    def test_check_eligibility_phone_hint(self) -> None:
        """未填写手机号时只提示，不阻断申请"""
        user = self.session.query(User).filter(User.id == 1).first()
        user.phone = None
        self.session.commit()

        result = ai_tools.check_adoption_eligibility(self.session, 1)

        self.assertTrue(result["ok"])
        self.assertTrue(result["eligible"])
        self.assertFalse(result["contact_ready"])
        self.assertIn("手机号", result["hint"])

    def test_submit_requires_confirm(self) -> None:
        """未确认时只返回确认指令，不写库"""
        result = ai_tools.submit_adoption_intent(
            db=self.session,
            user_id=1,
            pet_id=1,
            reason="家里有独立阳台并已封窗，每天可陪伴六小时。",
            auth_user_id=1,
        )

        self.assertTrue(result["need_confirm"])
        self.assertEqual(result["action"], "submit_adoption")
        self.assertEqual(self.session.query(AdoptionApplication).count(), 0)

    def test_submit_confirmed_creates_application(self) -> None:
        """确认后写入申请单"""
        result = ai_tools.submit_confirmed(
            db=self.session,
            user_id=1,
            pet_id=1,
            reason="家里有独立阳台并已封窗，每天可陪伴六小时。",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["application_id"], 1)
        self.assertEqual(self.session.query(AdoptionApplication).count(), 1)

    def test_submit_rejects_other_user(self) -> None:
        """伪造 user_id 必须被拒绝"""
        result = ai_tools.submit_adoption_intent(
            db=self.session,
            user_id=999,
            pet_id=1,
            reason="家里有独立阳台并已封窗，每天可陪伴六小时。",
            auth_user_id=1,
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "forbidden")

    def test_platform_stats(self) -> None:
        """统计工具返回猫狗数量"""
        result = ai_tools.get_platform_stats(self.session)

        self.assertTrue(result["ok"])
        self.assertEqual(result["pet_total"], 1)
        self.assertEqual(result["cat_total"], 1)
        self.assertEqual(result["dog_total"], 0)

    def test_build_tools_exposes_five_tools(self) -> None:
        """工具构建后应包含 5 个工具，且 partial 注入生效"""
        tools = ai_tools.build_tools(self.session, user_id=1)
        tool_map = ai_tools.get_tool_map(tools)

        self.assertEqual(set(tool_map.keys()), ai_tools.TOOL_NAMES)

        search_result = tool_map["search_pets"].invoke({"species": "猫"})
        self.assertTrue(search_result["ok"])
        self.assertEqual(search_result["total"], 1)

        confirm_result = tool_map["submit_adoption_intent"].invoke(
            {
                "user_id": 1,
                "pet_id": 1,
                "reason": "家里有独立阳台并已封窗，每天可陪伴六小时。",
            }
        )
        self.assertTrue(confirm_result["need_confirm"])

    def test_build_readonly_tools_excludes_submit(self) -> None:
        """第 3 步只绑定 4 个只读工具"""
        tools = ai_tools.build_readonly_tools(self.session, user_id=1)
        names = {tool.name for tool in tools}

        self.assertEqual(len(tools), 4)
        self.assertNotIn("submit_adoption_intent", names)
        self.assertEqual(
            names,
            {
                "search_pets",
                "get_pet_detail",
                "check_adoption_eligibility",
                "get_platform_stats",
            },
        )


if __name__ == "__main__":
    unittest.main()
