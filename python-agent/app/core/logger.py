"""
系统日志配置
作用: 配置项目统一的日志输出

loguru 的好处: 开箱即用, 输出彩色日志, 不用像内置 logging 一样写一堆配置
"""
import sys

from loguru import logger

from app.core.config import BASE_DIR

# 日志目录固定在项目根，避免从不同工作目录启动时日志散落
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 移除 loguru 默认的日志输出配置
logger.remove()

# 重新添加控制台输出
# format: 时间 | 级别 | 文件名:行号 | 日志内容
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# 同时把日志写入文件（每天一个文件，最多保留 7 天）
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    level="INFO",
    rotation="00:00",      # 每天 0 点创建新文件
    retention="7 days",    # 日志文件最多保留 7 天
    encoding="utf-8",      # 使用 utf-8 编码，避免中文乱码
)
