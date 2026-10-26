"""
构建 FAISS 向量库
作用:
1. 读取 docs/kb/*.md
2. 解析 YAML Front Matter
3. 按 # / ## / ### 标题切分，再按 500 字 / 50 字重叠二次切分
4. 生成 embedding 并持久化到 VECTOR_STORE_DIR

运行方式:
    python scripts/build_vectorstore.py
"""
import sys
from pathlib import Path

import yaml
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# 让脚本可以直接以 python scripts/build_vectorstore.py 运行
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.ai.vectorstore import save_index  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.logger import logger  # noqa: E402


KB_DIR = BASE_DIR / "docs" / "kb"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MIN_CHUNK_LENGTH = 80


def parse_front_matter(text: str) -> tuple[dict, str]:
    """拆分 YAML Front Matter 与正文"""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    return meta, body


def load_documents() -> list[Document]:
    """读取 docs/kb 下所有 Markdown，返回带元数据的文档"""
    documents: list[Document] = []

    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)

        doc_id = meta.get("doc_id") or f"kb-{path.stem}"
        title = meta.get("title") or path.stem
        category = meta.get("category") or "adoption"

        documents.append(
            Document(
                page_content=body,
                metadata={
                    "doc_id": doc_id,
                    "title": title,
                    "category": category,
                    "source": meta.get("source") or f"docs/kb/{path.name}",
                    "updated_at": str(meta.get("updated_at") or ""),
                    "version": str(meta.get("version") or "1.0"),
                    "priority": int(meta.get("priority") or 0),
                },
            )
        )

    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """先按标题切分，再按长度切分，最后合并过短的块"""
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    length_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", " "],
        keep_separator=True,
    )

    chunks: list[Document] = []

    for doc in documents:
        sections = header_splitter.split_text(doc.page_content)

        for section in sections:
            # 标题路径: 领养条件与申请流程 > 基本条件 > 租房家庭
            title_parts = [
                section.metadata.get(key, "")
                for key in ("h1", "h2", "h3")
                if section.metadata.get(key)
            ]
            # 一级标题通常与文档标题重复，这里只保留二级及以下
            section_path = " > ".join(title_parts[1:]) if len(title_parts) > 1 else ""
            prefix = f"{doc.metadata['title']}"
            if section_path:
                prefix = f"{prefix} > {section_path}"

            for piece in length_splitter.split_text(section.page_content):
                content = piece.strip()
                if not content:
                    continue

                chunks.append(
                    Document(
                        page_content=f"【{prefix}】\n{content}",
                        metadata={
                            **doc.metadata,
                            "section": section_path,
                            "content": content,
                        },
                    )
                )

    return merge_small_chunks(chunks)


def merge_small_chunks(chunks: list[Document]) -> list[Document]:
    """小于 80 字的块合并到上一块，避免出现碎片"""
    merged: list[Document] = []

    for chunk in chunks:
        if merged and len(chunk.metadata.get("content", "")) < MIN_CHUNK_LENGTH:
            previous = merged[-1]
            previous.page_content = f"{previous.page_content}\n{chunk.metadata['content']}"
            previous.metadata["content"] = (
                f"{previous.metadata.get('content', '')}\n{chunk.metadata['content']}"
            )
            continue

        merged.append(chunk)

    return merged


def build() -> None:
    """执行建库流程"""
    if not KB_DIR.exists():
        raise FileNotFoundError(f"知识库目录不存在: {KB_DIR}")

    raw_docs = load_documents()
    if not raw_docs:
        raise ValueError("docs/kb 下没有可用的 Markdown 文档")

    chunks = split_documents(raw_docs)
    logger.info(f"知识库文档 {len(raw_docs)} 篇，切分后共 {len(chunks)} 个 chunk")

    # 补充分块序号与 chunk_id，便于回答时引用
    counters: dict[str, int] = {}
    for chunk in chunks:
        doc_id: str = chunk.metadata["doc_id"]
        index: int = counters.get(doc_id, 0)
        chunk.metadata["chunk_index"] = index
        chunk.metadata["chunk_id"] = f"{doc_id}-{index:03d}"
        counters[doc_id] = index + 1

    vectorstore = save_index(chunks)
    logger.info(
        f"向量库已写入: {settings.vector_store_path}，向量数: {vectorstore.index.ntotal}"
    )

    print("建库完成")
    print(f"文档数: {len(raw_docs)}")
    print(f"分块数: {len(chunks)}")
    print(f"向量库目录: {settings.vector_store_path}")

    for doc in raw_docs:
        count = sum(
            1 for chunk in chunks if chunk.metadata["doc_id"] == doc.metadata["doc_id"]
        )
        print(f"  - {doc.metadata['doc_id']} {doc.metadata['title']}: {count} 块")


if __name__ == "__main__":
    build()
