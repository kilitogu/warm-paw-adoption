"""
全局大模型封装
作用: 统一创建 ChatOpenAI 与 Embedding 模型，避免每个模块重复读取配置
"""
from functools import lru_cache
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings


@lru_cache(maxsize=1)
def get_chat_model() -> ChatOpenAI:
    """
    获取全局对话模型

    streaming=True: 让 LangGraph 的 astream_events 能拿到 on_chat_model_stream 事件
    """
    if not settings.llm_api_key:
        raise RuntimeError("未配置 LLM_API_KEY，请在 .env 中补充后重启服务")

    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=settings.llm_temperature,
        streaming=True,
        timeout=settings.llm_timeout,
        max_retries=2,
    )


@lru_cache(maxsize=1)
def get_embedding_model() -> Embeddings:
    """
    获取全局向量模型

    注意: 建库脚本与在线检索必须使用同一个模型，否则向量空间不一致。

    - embedding_provider=openai: 走 OpenAI 兼容的 /embeddings 接口（推荐）
    - embedding_provider=huggingface: 使用本地 sentence-transformers 模型，
      需要额外安装 requirements-local-embed.txt
    """
    provider: str = settings.embedding_provider.strip().lower()

    if provider == "huggingface":
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError as exc:  # pragma: no cover - 取决于本机可选依赖
            raise RuntimeError(
                "本地向量模型需要先安装可选依赖: "
                "pip install -r requirements-local-embed.txt"
            ) from exc

        return HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": settings.embedding_device},
            encode_kwargs={"normalize_embeddings": True},
        )

    if not settings.embedding_key:
        raise RuntimeError("未配置 EMBEDDING_API_KEY（或 LLM_API_KEY），无法生成向量")

    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.embedding_key,
        base_url=settings.embedding_base,
        timeout=settings.llm_timeout,
        max_retries=2,
    )


def get_ai_status() -> dict[str, Any]:
    """返回 AI 配置摘要，供健康检查接口使用（不泄露密钥）"""
    return {
        "llm_model": settings.llm_model,
        "llm_configured": bool(settings.llm_api_key),
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model,
        "embedding_configured": bool(settings.embedding_key),
        "vector_store_dir": settings.vector_store_path,
    }
