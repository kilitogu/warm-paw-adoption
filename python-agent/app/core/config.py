"""
程序基本配置
作用: 读取 .env 文件中的配置项, 供整个项目使用
相当于整个系统的"配置读取中心"
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录: app/core/config.py -> app/core -> app -> 项目根
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 上传文件限制
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 静态资源目录: 项目根/uploads
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 允许上传的文件后缀
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip",
}


class Settings(BaseSettings):
    """全局配置项，字段名与 .env 中的变量名一一对应（不区分大小写）"""

    # 告诉 pydantic_settings: 去哪里读取配置文件
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用信息
    app_name: str = "暖爪 · 智能宠物领养平台"
    fast_profile: str = "./file"

    # 数据库配置
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "pet_agent"
    db_user: str = "root"
    db_password: str = ""

    # 后端端口
    server_port: int = 8080

    # 跨域白名单，多个来源用英文逗号分隔
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # token 配置
    # 请求头的字段名: 前端需要在请求头携带此字段传递 token
    token_header: str = "Authorization"
    # 令牌密钥: 前后端约定好的"暗号", 用于加密/解密 token
    token_secret: str = ""
    # 令牌有效期(小时), 过期后需要重新登录
    token_expire_hours: int = 24
    # 加密算法默认为 "HS256"
    token_algorithm: str = "HS256"

    # ===== AI 助手配置 =====
    # 兼容 OpenAI 协议的大模型服务
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    llm_timeout: int = 60
    llm_temperature: float = 0.3

    # 向量模型: openai(兼容接口) / huggingface(本地模型)
    embedding_provider: str = "openai"
    # 留空时复用 LLM 的密钥与地址
    embedding_api_key: str = ""
    embedding_base_url: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_device: str = "cpu"

    # 向量库目录与检索参数
    vector_store_dir: str = "./data/vectorstore"
    rag_top_k: int = 4
    rag_score_threshold: float = 0.35
    # 会话空闲多久后清理（LangGraph MemorySaver 进程内保存）
    ai_session_ttl_minutes: int = 30

    @property
    def database_url(self) -> str:
        """
        数据库连接地址(pymysql 格式)

        拼接后的完整地址类似:
        mysql+pymysql://root:密码@localhost:3306/pet_agent?charset=utf8mb4
        """
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    @property
    def vector_store_path(self) -> str:
        """
        向量库绝对路径
        允许在 .env 中写相对路径，统一转换为基于项目根目录的绝对路径
        """
        path = Path(self.vector_store_dir)
        return str(path if path.is_absolute() else BASE_DIR / path)

    @property
    def embedding_key(self) -> str:
        """向量模型密钥，未单独配置时复用 LLM 密钥"""
        return self.embedding_api_key or self.llm_api_key

    @property
    def embedding_base(self) -> str:
        """向量模型接口地址，未单独配置时复用 LLM 地址"""
        return self.embedding_base_url or self.llm_base_url

    @property
    def cors_origin_list(self) -> list[str]:
        """把逗号分隔的白名单转换成列表"""
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


# 创建全局配置对象: 其他文件直接 from app.core.config import settings 使用即可
settings = Settings()
