"""
向量库底层读写
作用: 统一 FAISS 索引的加载、保存与存在性判断
"""
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document

from app.core.config import settings
from app.core.llm import get_embedding_model
from app.core.logger import logger

# 索引文件名固定，加载与保存必须一致
INDEX_NAME: str = "index"


def index_exists() -> bool:
    """判断向量库文件是否存在"""
    base = Path(settings.vector_store_path)
    return (base / f"{INDEX_NAME}.faiss").exists() and (
        base / f"{INDEX_NAME}.pkl"
    ).exists()


def save_index(documents: list[Document]) -> FAISS:
    """把文档切片写入 FAISS 并持久化"""
    if not documents:
        raise ValueError("没有可写入向量库的文档")

    embeddings = get_embedding_model()

    # normalize_L2 + COSINE: 让相似度分数稳定落在 0-1，便于设置阈值
    vectorstore = FAISS.from_documents(
        documents,
        embeddings,
        normalize_L2=True,
        distance_strategy=DistanceStrategy.COSINE,
    )

    target = Path(settings.vector_store_path)
    target.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(target), index_name=INDEX_NAME)

    logger.info(
        f"向量库写入完成 | path={target} | vectors={vectorstore.index.ntotal}"
    )
    return vectorstore


def load_index() -> FAISS | None:
    """加载本地 FAISS 索引，不存在时返回 None"""
    if not index_exists():
        logger.warning(
            f"向量库不存在: {settings.vector_store_path}，请先运行 scripts/build_vectorstore.py"
        )
        return None

    embeddings = get_embedding_model()
    vectorstore = FAISS.load_local(
        settings.vector_store_path,
        embeddings,
        index_name=INDEX_NAME,
        allow_dangerous_deserialization=True,  # 本地自建索引，允许反序列化
    )

    return vectorstore
