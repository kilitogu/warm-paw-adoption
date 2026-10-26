"""
知识库切分脚本的离线测试
作用: 不依赖 Embedding 接口，验证 Front Matter 解析与 chunk 切分规则

运行方式:
    python -m unittest discover -s tests -v
"""
import sys
import unittest
from pathlib import Path

from langchain_core.documents import Document

# scripts 目录没有 __init__.py，直接按文件路径导入
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import build_vectorstore as kb  # noqa: E402


class KnowledgeBaseTestCase(unittest.TestCase):
    def test_parse_front_matter(self) -> None:
        """Front Matter 应被正确解析，正文不包含分隔符"""
        text = "---\ndoc_id: kb-test-001\ntitle: 测试文档\n---\n\n# 标题\n\n正文"

        meta, body = kb.parse_front_matter(text)

        self.assertEqual(meta["doc_id"], "kb-test-001")
        self.assertEqual(meta["title"], "测试文档")
        self.assertTrue(body.startswith("# 标题"))

    def test_parse_without_front_matter(self) -> None:
        """没有 Front Matter 时原样返回"""
        meta, body = kb.parse_front_matter("# 标题\n\n正文")

        self.assertEqual(meta, {})
        self.assertEqual(body, "# 标题\n\n正文")

    def test_split_documents_prefix_title(self) -> None:
        """每个 chunk 应带上文档标题与章节路径"""
        doc = Document(
            page_content=(
                "# 领养条件\n\n## 基本条件\n\n"
                "申请人必须年满 18 周岁，具有完全民事行为能力，并提供稳定的住所证明。"
            ),
            metadata={
                "doc_id": "kb-adoption-001",
                "title": "领养条件与申请流程",
                "category": "adoption",
                "source": "docs/kb/adoption-guide.md",
                "priority": 10,
            },
        )

        chunks = kb.split_documents([doc])

        self.assertTrue(chunks)
        self.assertTrue(chunks[0].page_content.startswith("【领养条件与申请流程"))
        self.assertIn("基本条件", chunks[0].metadata["section"])

    def test_load_documents_from_repo(self) -> None:
        """仓库自带的 4 篇知识库文档应可被读取"""
        documents = kb.load_documents()

        self.assertGreaterEqual(len(documents), 4)
        self.assertTrue(
            {"adoption", "faq", "care", "rule"}
            <= {doc.metadata["category"] for doc in documents}
        )

    def test_chunk_metadata(self) -> None:
        """切分后的 chunk 应带标题前缀，且正文不为空"""
        chunks = kb.split_documents(kb.load_documents())

        self.assertTrue(chunks)
        for chunk in chunks:
            self.assertTrue(chunk.page_content.strip())
            self.assertTrue(chunk.page_content.startswith("【"))


if __name__ == "__main__":
    unittest.main()
