"""
RAG 检索器
作用:
1. 单例加载 FAISS 向量库，避免每次对话重复读盘
2. 按 query 召回 Top-K 片段，并按相似度阈值过滤
3. 无命中时返回空列表，由上层执行降级策略
"""
import threading

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.ai.vectorstore import load_index
from app.core.config import settings
from app.core.logger import logger

# 进程内单例
_vectorstore: FAISS | None = None
_lock = threading.Lock()


def load_vectorstore(force_reload: bool = False) -> FAISS | None:
    """单例加载向量库；force_reload=True 用于重建索引后热更新"""
    global _vectorstore

    if _vectorstore is not None and not force_reload:
        return _vectorstore

    with _lock:
        if _vectorstore is not None and not force_reload:
            return _vectorstore

        _vectorstore = load_index()

        if _vectorstore is None:
            logger.warning("向量库未加载，RAG 检索将返回空结果")
        else:
            logger.info(f"向量库加载完成，向量数: {_vectorstore.index.ntotal}")

        return _vectorstore


def retrieve(query: str, top_k: int | None = None) -> list[Document]:
    """
    检索相关文档片段

    :param query: 用户问题
    :param top_k: 召回条数，默认读取 RAG_TOP_K
    :return: 相似度达标的 Document 列表，无命中返回 []
    """
    if not query or not query.strip():
        return []

    vectorstore = load_vectorstore()
    if vectorstore is None:
        return []

    k: int = top_k or settings.rag_top_k

    try:
        pairs = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    except Exception:
        logger.exception("RAG 检索失败")
        return []

    documents: list[Document] = []
    for doc, score in pairs:
        score_value = float(score)
        if score_value < settings.rag_score_threshold:
            continue

        doc.metadata["score"] = round(score_value, 4)
        documents.append(doc)

    top_score = round(float(pairs[0][1]), 4) if pairs else 0.0
    logger.info(
        f"RAG 检索 | query={query[:40]} | top_k={k} | 命中={len(documents)} | 最高分={top_score}"
    )

    return documents


def format_sources(documents: list[Document]) -> list[dict]:
    """转换成 SSE retrieval 事件的 sources 字段"""
    sources: list[dict] = []

    for doc in documents:
        sources.append(
            {
                "title": doc.metadata.get("title") or "未命名文档",
                "section": doc.metadata.get("section") or "",
                "snippet": doc.metadata.get("content", doc.page_content)[:180],
                "source": doc.metadata.get("source") or "",
                "score": doc.metadata.get("score", 0.0),
            }
        )

    return sources
