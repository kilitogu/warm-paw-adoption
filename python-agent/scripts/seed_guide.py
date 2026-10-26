"""
领养指南 FAQ 初始化脚本
作用: 写入 12 条常见问题，供 Guide.vue 与 RAG 知识库使用

运行方式:
    python scripts/seed_guide.py
    python scripts/seed_guide.py --force
"""
import argparse
import sys
from pathlib import Path

# 让脚本可以直接以 python scripts/seed_guide.py 运行
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import app.models  # noqa: E402,F401
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.guide import GuideFaq  # noqa: E402


FAQS: list[dict] = [
    {
        "category": "领养条件",
        "question": "领养人需要满足哪些基本条件？",
        "answer": "年满 18 周岁、有稳定住所与收入、家庭成员全部同意养宠、接受封窗与家访、承诺科学喂养并按时接种疫苗。租住房屋需提供房东同意养宠的证明。",
        "sort_order": 1,
    },
    {
        "category": "领养条件",
        "question": "学生或刚毕业可以领养吗？",
        "answer": "可以，但需要提供稳定的经济来源证明，并说明毕业、搬家、寒暑假等阶段的宠物安置方案。未独立居住的学生需取得共同居住人书面同意。",
        "sort_order": 2,
    },
    {
        "category": "领养条件",
        "question": "领养需要支付费用吗？",
        "answer": "平台不收取任何领养费。部分救助站会收取已垫付的疫苗、绝育、驱虫成本，金额在宠物详情页公开，并提供正规票据。",
        "sort_order": 3,
    },
    {
        "category": "申请流程",
        "question": "提交申请后多久会收到回复？",
        "answer": "志愿者通常在 48 小时内通过电话或微信联系。若 3 个工作日未收到回复，可在“我的申请”中查看进度或联系在线客服。",
        "sort_order": 1,
    },
    {
        "category": "申请流程",
        "question": "可以同时申请多只宠物吗？",
        "answer": "可以，但最多同时保留 3 条待审核申请。建议优先选择最匹配的一只，避免占用多个救助站的沟通资源。",
        "sort_order": 2,
    },
    {
        "category": "申请流程",
        "question": "审核通过后需要做什么？",
        "answer": "审核通过后需签署领养协议、完成家访或视频看房，并确认疫苗与绝育安排。接宠物时请自备航空箱、牵引绳与过渡粮。",
        "sort_order": 3,
    },
    {
        "category": "申请流程",
        "question": "申请被拒绝后还能再次申请吗？",
        "answer": "可以。拒绝通常与居住环境、家庭成员意见或时间安排有关，建议根据志愿者反馈调整后再申请，同一只宠物 30 天内不重复受理。",
        "sort_order": 4,
    },
    {
        "category": "宠物健康",
        "question": "领养前能查看疫苗和体检记录吗？",
        "answer": "可以。详情页会展示疫苗接种、驱虫、绝育与体检结论。未展示的项目可在沟通阶段向志愿者索取纸质或电子记录。",
        "sort_order": 1,
    },
    {
        "category": "宠物健康",
        "question": "领养后发现健康问题怎么办？",
        "answer": "领养后 7 天内发现的传染性疾病或先天性疾病，由原救助站承担首次诊疗费用；慢性病与意外伤害由领养人承担，平台可协助对接合作医院。",
        "sort_order": 2,
    },
    {
        "category": "领养后",
        "question": "领养后需要接受回访吗？",
        "answer": "需要。领养后第 1 周、第 1 个月、第 3 个月各有一次回访，形式为照片/视频或上门家访，用于确认宠物适应情况。",
        "sort_order": 1,
    },
    {
        "category": "领养后",
        "question": "如果实在无法继续饲养怎么办？",
        "answer": "严禁弃养或私自转送。请第一时间联系原救助站，由平台协助重新寻找领养家庭。弃养行为会被记入黑名单并终止后续领养资格。",
        "sort_order": 2,
    },
    {
        "category": "领养后",
        "question": "领养后需要给宠物做绝育吗？",
        "answer": "需要。除非兽医出具不适合手术的证明，否则应在适龄阶段完成绝育。绝育不仅是健康管理，也能减少走失与无序繁殖。",
        "sort_order": 3,
    },
]


def seed(force: bool = False) -> None:
    """写入 FAQ 种子数据"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        exists: int = db.query(GuideFaq).count()
        if exists > 0 and not force:
            print(f"guide_faqs 表已有 {exists} 条数据，跳过写入。如需重建请加 --force")
            return

        if force:
            db.query(GuideFaq).delete()
            db.commit()
            print("已清空 guide_faqs 表")

        for item in FAQS:
            db.add(GuideFaq(**item))
        db.commit()

        total: int = db.query(GuideFaq).count()
        print(f"FAQ 数据写入完成，当前共 {total} 条")
    except Exception as exc:
        db.rollback()
        print(f"写入失败: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化领养指南 FAQ")
    parser.add_argument("--force", action="store_true", help="清空 FAQ 表后重新写入")
    args = parser.parse_args()
    seed(force=args.force)
