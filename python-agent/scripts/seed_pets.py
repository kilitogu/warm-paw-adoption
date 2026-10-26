"""
宠物测试数据初始化脚本
作用: 向 pets 表写入 14 条样例数据，供首页推荐、宠物列表、AI 检索联调使用

运行方式:
    python scripts/seed_pets.py
    python scripts/seed_pets.py --force   # 清空后重新写入
"""
import argparse
import sys
from pathlib import Path

# 让脚本可以直接以 python scripts/seed_pets.py 运行
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import app.models  # noqa: E402,F401
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.pet import Pet  # noqa: E402


PETS: list[dict] = [
    {
        "name": "奶糖", "species": "猫", "breed": "布偶猫", "gender": "母",
        "age_months": 8, "city": "杭州", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 326,
        "description": "被人遗弃在小区车库，性格黏人，喜欢被抱着睡觉，和其他猫相处友好。",
        "cover_image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800",
        "images": [
            "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=1200",
            "https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=1200",
            "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=1200",
        ],
    },
    {
        "name": "豆豆", "species": "狗", "breed": "柯基", "gender": "公",
        "age_months": 14, "city": "上海", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 289,
        "description": "前主人搬家无法带走，性格活泼，会坐下和握手，每天需要两次遛弯。",
        "cover_image": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=800",
        "images": [
            "https://images.unsplash.com/photo-1552053831-71594a27632d?w=1200",
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=1200",
        ],
    },
    {
        "name": "年糕", "species": "猫", "breed": "英国短毛猫", "gender": "公",
        "age_months": 24, "city": "北京", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 412,
        "description": "救助站出生的二代猫，性格稳定，不拆家，适合上班族家庭。",
        "cover_image": "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=800",
        "images": [
            "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=1200",
            "https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=1200",
        ],
    },
    {
        "name": "可乐", "species": "狗", "breed": "金毛寻回犬", "gender": "公",
        "age_months": 36, "city": "成都", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 501,
        "description": "性格温顺的大暖男，亲人不怕生，适合有院子或有大块活动时间的家庭。",
        "cover_image": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=800&sat=-20",
        "images": [
            "https://images.unsplash.com/photo-1552053831-71594a27632d?w=1200&sat=-20",
            "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=1200",
        ],
    },
    {
        "name": "芝麻", "species": "猫", "breed": "中华田园猫", "gender": "母",
        "age_months": 6, "city": "南京", "health_status": "亚健康",
        "vaccinated": True, "sterilized": False, "status": "可领养", "view_count": 198,
        "description": "流浪时有点营养不良，经过一个月调理已明显好转，需要继续补充营养。",
        "cover_image": "https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=800",
        "images": [
            "https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=1200",
            "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=1200",
        ],
    },
    {
        "name": "汤圆", "species": "狗", "breed": "比熊犬", "gender": "母",
        "age_months": 20, "city": "广州", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 245,
        "description": "小型犬，掉毛少，性格安静，适合公寓饲养，已学会定点上厕所。",
        "cover_image": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800",
        "images": [
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=1200",
            "https://images.unsplash.com/photo-1596492784531-6e6eb5ea9993?w=1200",
        ],
    },
    {
        "name": "布丁", "species": "猫", "breed": "橘猫", "gender": "公",
        "age_months": 30, "city": "杭州", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 377,
        "description": "胃口好、性格好，见人就翻肚皮，需要控制体重，每天定时定量喂食。",
        "cover_image": "https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=800",
        "images": [
            "https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=1200",
            "https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=1200",
        ],
    },
    {
        "name": "闪电", "species": "狗", "breed": "边境牧羊犬", "gender": "公",
        "age_months": 18, "city": "深圳", "health_status": "健康",
        "vaccinated": True, "sterilized": False, "status": "可领养", "view_count": 333,
        "description": "精力旺盛、学习能力强，需要每天至少一小时运动，不适合长期笼养。",
        "cover_image": "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=800",
        "images": [
            "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=1200",
            "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=1200",
        ],
    },
    {
        "name": "雪球", "species": "狗", "breed": "萨摩耶", "gender": "母",
        "age_months": 48, "city": "北京", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 456,
        "description": "微笑天使，亲人但掉毛量大，需要每周梳毛三次，希望找到有耐心的家庭。",
        "cover_image": "https://images.unsplash.com/photo-1596492784531-6e6eb5ea9993?w=800",
        "images": [
            "https://images.unsplash.com/photo-1596492784531-6e6eb5ea9993?w=1200",
            "https://images.unsplash.com/photo-1552053831-71594a27632d?w=1200",
        ],
    },
    {
        "name": "花卷", "species": "猫", "breed": "狸花猫", "gender": "母",
        "age_months": 12, "city": "武汉", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 167,
        "description": "小区 TNR 救助的猫咪，独立但不孤僻，适合有养猫经验、能提供安静环境的家庭。",
        "cover_image": "https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=800",
        "images": [
            "https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=1200",
            "https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=1200",
        ],
    },
    {
        "name": "阿福", "species": "狗", "breed": "柴犬", "gender": "公",
        "age_months": 26, "city": "上海", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 298,
        "description": "性格独立、爱干净，出门需要牵引，适合了解柴犬性格、能坚持训练的家庭。",
        "cover_image": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=800",
        "images": [
            "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=1200",
            "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=1200",
        ],
    },
    {
        "name": "小满", "species": "猫", "breed": "美国短毛猫", "gender": "母",
        "age_months": 9, "city": "成都", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 221,
        "description": "活泼好动，喜欢逗猫棒，能和其他猫共享猫砂盆，适合首次养猫的家庭。",
        "cover_image": "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=800&sat=-30",
        "images": [
            "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=1200&sat=-30",
            "https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=1200",
        ],
    },
    {
        "name": "黑豆", "species": "狗", "breed": "拉布拉多", "gender": "公",
        "age_months": 60, "city": "南京", "health_status": "需治疗",
        "vaccinated": True, "sterilized": True, "status": "可领养", "view_count": 143,
        "description": "老年犬，患有轻度关节炎，需要长期服药和软垫休息，医疗费用由救助站承担。",
        "cover_image": "https://images.unsplash.com/photo-1596492784531-6e6eb5ea9993?w=800&sat=-40",
        "images": [
            "https://images.unsplash.com/photo-1596492784531-6e6eb5ea9993?w=1200&sat=-40",
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=1200",
        ],
    },
    {
        "name": "团子", "species": "猫", "breed": "暹罗猫", "gender": "公",
        "age_months": 15, "city": "广州", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "已领养", "view_count": 264,
        "description": "已于 2026 年 3 月被领养，保留数据用于展示领养成功案例。",
        "cover_image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800&sat=-30",
        "images": [
            "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=1200&sat=-30",
        ],
    },
    {
        "name": "七喜", "species": "狗", "breed": "泰迪", "gender": "母",
        "age_months": 33, "city": "武汉", "health_status": "健康",
        "vaccinated": True, "sterilized": True, "status": "已领养", "view_count": 208,
        "description": "已于 2026 年 2 月被领养，保留数据用于统计累计领养数量。",
        "cover_image": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800&sat=-40",
        "images": [
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=1200&sat=-40",
        ],
    },
]


def seed(force: bool = False) -> None:
    """写入种子数据；force=True 时先清空 pets 表"""
    # 确保表已创建
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        exists: int = db.query(Pet).count()
        if exists > 0 and not force:
            print(f"pets 表已有 {exists} 条数据，跳过写入。如需重建请加 --force")
            return

        if force:
            db.query(Pet).delete()
            db.commit()
            print("已清空 pets 表")

        for item in PETS:
            db.add(Pet(**item))
        db.commit()

        total: int = db.query(Pet).count()
        print(f"宠物测试数据写入完成，当前共 {total} 条")
    except Exception as exc:
        db.rollback()
        print(f"写入失败: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化宠物测试数据")
    parser.add_argument("--force", action="store_true", help="清空 pets 表后重新写入")
    args = parser.parse_args()
    seed(force=args.force)
