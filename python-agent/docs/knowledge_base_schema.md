# 暖爪知识库语料 Schema

版本：v1.0
适用范围：领养指南、FAQ、宠物养护知识、平台规则
维护人：内容运营 + 后端

## 1. 设计目标

1. 每篇文档都能独立追溯到来源，便于回答用户时给出引用。
2. 字段结构同时适配 MySQL 元数据表与向量库 metadata，不做二次转换。
3. 分块规则固定，保证每次重建向量库的切分结果一致。

## 2. 文档元数据字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| doc_id | string | 是 | 全局唯一文档ID，格式 `kb-{分类}-{三位序号}`，例如 `kb-adoption-001` |
| title | string | 是 | 文档标题，与一级标题保持一致 |
| category | string | 是 | 分类枚举：`adoption` / `faq` / `care` / `rule` |
| content | string | 是 | 文档正文，Markdown 格式，UTF-8 编码 |
| source | string | 是 | 来源路径或链接，例如 `docs/kb/adoption-guide.md` |
| updated_at | string | 是 | 最后更新时间，ISO 8601 格式 `YYYY-MM-DD` |
| version | string | 否 | 文档版本号，默认 `1.0` |
| tags | string[] | 否 | 检索标签，例如 `["封窗","租房","学生"]` |
| priority | int | 否 | 排序优先级，数值越大越优先，默认 0 |

## 3. 单篇文档格式

每篇 Markdown 文件由 YAML Front Matter 与正文组成，Front Matter 必须位于文件第一行：

```yaml
---
doc_id: kb-adoption-001
title: 领养条件与申请流程
category: adoption
source: docs/kb/adoption-guide.md
updated_at: 2026-10-20
version: 1.0
tags: ["领养条件", "申请流程", "材料"]
priority: 10
---

# 领养条件与申请流程

## 基本条件

正文内容示例：申请人需年满 18 周岁，并提供稳定住所证明。
```

## 4. 分块规则

| 配置项 | 取值 | 说明 |
|---|---|---|
| 切分方式 | 先按标题切分，再按长度切分 | 一级到三级标题均作为切分边界 |
| chunk_size | 500 | 以字符数计，约 300 - 400 个汉字 |
| chunk_overlap | 50 | 相邻块重叠 50 个字符，避免语义被截断 |
| 最小块长度 | 80 | 小于 80 字符的块合并到上一块 |
| 分隔符优先级 | `\n## ` → `\n### ` → `\n\n` → `\n` → `。` | 逐级降级，优先保持段落完整 |
| 标题保留 | 是 | 每个 chunk 的正文前拼接所属标题路径 |

标题路径拼接示例：

```text
领养条件与申请流程 > 基本条件 > 租房家庭
```

## 5. Chunk 元数据

每个 chunk 在文档元数据基础上追加以下字段：

| 字段 | 说明 |
|---|---|
| chunk_id | `{doc_id}-{序号}`，例如 `kb-adoption-001-003` |
| chunk_index | 块在文档中的顺序，从 0 开始 |
| section | 标题路径，用于回答时展示“出自哪一节” |
| content | 块正文（含标题路径前缀） |

## 6. 入库流程

```text
docs/kb/*.md
    ↓ 读取 Front Matter
    ↓ MarkdownHeaderTextSplitter 按 # / ## / ### 切分
    ↓ RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50) 二次切分
    ↓ 拼接标题路径 + 继承文档元数据
    ↓ Embedding 模型生成向量（OpenAI 兼容接口或本地模型）
    ↓ FAISS 持久化到 VECTOR_STORE_DIR
```

## 7. 质量要求

1. 一篇文档只讲一个主题，超过 3000 字拆成多篇。
2. 不使用“如上文”“见下节”等依赖上下文的表述，保证 chunk 独立可读。
3. 数字、金额、时限必须写明确，例如“48 小时内”而不是“尽快”。
4. 医疗相关内容必须注明“建议咨询执业兽医”。
5. 平台规则变更时同步更新 `updated_at` 与 `version`，并重建向量库。

## 8. 分类与命名

| category | 目录 | 示例 doc_id |
|---|---|---|
| adoption | docs/kb/adoption-guide.md | kb-adoption-001 |
| faq | docs/kb/faq.md | kb-faq-001 |
| care | docs/kb/pet-care.md | kb-care-001 |
| rule | docs/kb/platform-rules.md | kb-rule-001 |
