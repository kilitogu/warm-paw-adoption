"""
AI 助手接口
作用:
1. POST /api/ai/chat：接收用户消息，把 LangGraph 的事件映射为 SSE
2. POST /api/ai/confirm：接收二次确认结果，恢复被 interrupt 暂停的图
3. GET  /api/ai/health：返回 AI 配置与向量库状态，便于部署自检
"""
import asyncio
import time
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from langchain_core.messages import AIMessage
from langgraph.types import Command
from sse_starlette.sse import EventSourceResponse

from app.ai.graph import build_thread_id, build_turn_input, get_graph, touch_thread
from app.ai.sse import (
    sse_confirm,
    sse_done,
    sse_error,
    sse_intent,
    sse_meta,
    sse_retrieval,
    sse_token,
    sse_tool_end,
    sse_tool_start,
)
from app.ai.tools import TOOL_NAMES
from app.ai.vectorstore import index_exists
from app.core.database import SessionLocal
from app.core.llm import get_ai_status
from app.core.logger import logger
from app.dependencies.deps import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest, ConfirmRequest

router = APIRouter(prefix="/api/ai", tags=["AI助手"])

SSE_HEADERS: dict[str, str] = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # 关闭 Nginx 缓冲，保证逐字输出
}


def _summarize_tool_result(tool_name: str, result: object) -> str:
    """把工具结果压缩成一句摘要，供 tool_end 事件展示"""
    if not isinstance(result, dict):
        return str(result)[:120]

    if result.get("need_confirm"):
        return "等待用户确认"

    if not result.get("ok"):
        return str(result.get("error") or "执行失败")[:120]

    if tool_name == "search_pets":
        return f"找到 {result.get('count', 0)} 只宠物"
    if tool_name == "get_pet_detail":
        pet = result.get("pet") or {}
        return f"已获取「{pet.get('name', '')}」的详情"
    if tool_name == "check_adoption_eligibility":
        if result.get("eligible"):
            return "资格校验通过"
        return f"缺少 {len(result.get('missing', []))} 项条件"
    if tool_name == "submit_adoption_intent":
        application_id = result.get("application_id")
        return f"申请单号 {application_id}" if application_id else "申请已提交"
    if tool_name == "get_platform_stats":
        return (
            f"在架 {result.get('pet_total', 0)} 只，"
            f"累计领养 {result.get('adopted_total', 0)} 只"
        )

    return "执行完成"


async def _stream_events(
    graph,
    payload,
    config: dict,
    request: Request,
    session_id: str,
    query_text: str = "",
) -> AsyncGenerator[dict, None]:
    """
    把 LangGraph 的 astream_events 映射为 SSE 事件

    token 事件来自 on_chat_model_stream，工具事件来自 on_tool_start / on_tool_end
    """
    started_at: float = time.perf_counter()
    token_sent: bool = False

    yield sse_meta(session_id)

    try:
        async for event in graph.astream_events(payload, config=config, version="v2"):
            if await request.is_disconnected():
                logger.info(f"客户端已断开 | session_id={session_id}")
                return

            kind: str = event.get("event", "")
            name: str = event.get("name", "")
            metadata: dict = event.get("metadata") or {}
            node: str | None = metadata.get("langgraph_node")

            # 1. 意图识别完成
            if kind == "on_chain_end" and name == "intent_router":
                output = event.get("data", {}).get("output") or {}
                intent = output.get("intent")
                if intent:
                    yield sse_intent(intent)

            # 2. RAG 检索完成
            elif kind == "on_chain_end" and name == "rag_retrieve":
                output = event.get("data", {}).get("output") or {}
                documents = output.get("retrieved_docs") or []
                sources = [
                    {
                        "title": doc.get("title", ""),
                        "section": doc.get("section", ""),
                        "snippet": doc.get("snippet", ""),
                        "source": doc.get("source", ""),
                        "score": doc.get("score", 0.0),
                    }
                    for doc in documents
                ]
                yield sse_retrieval(query_text, sources)

            # 3. 工具调用开始
            elif kind == "on_tool_start" and name in TOOL_NAMES:
                args = event.get("data", {}).get("input") or {}
                yield sse_tool_start(name, args)

            # 4. 工具调用结束
            elif kind == "on_tool_end" and name in TOOL_NAMES:
                output = event.get("data", {}).get("output")
                yield sse_tool_end(name, _summarize_tool_result(name, output))

            # 4.1 资格校验 / 二次确认节点内部直接调用了工具，这里补发工具事件
            elif kind == "on_chain_end" and name in (
                "check_adoption_eligibility",
                "confirm_apply",
            ):
                output = event.get("data", {}).get("output") or {}
                for item in output.get("tool_results") or []:
                    yield sse_tool_start(item.get("tool", ""), item.get("args") or {})
                    yield sse_tool_end(
                        item.get("tool", ""),
                        _summarize_tool_result(item.get("tool", ""), item.get("result")),
                    )

            # 5. 只转发 answer / human_handoff 节点的 token
            elif kind == "on_chat_model_stream" and node in ("answer", "human_handoff"):
                chunk = event.get("data", {}).get("chunk")
                content = getattr(chunk, "content", "")
                if content:
                    token_sent = True
                    yield sse_token(str(content))

        # 流结束后检查是否停在 interrupt
        snapshot = await graph.aget_state(config)
        values = snapshot.values or {}

        interrupt_payload = None
        for task in getattr(snapshot, "tasks", None) or []:
            interrupts = getattr(task, "interrupts", None) or []
            if interrupts:
                interrupt_payload = interrupts[0].value
                break

        if interrupt_payload:
            yield sse_confirm(interrupt_payload)
        elif not token_sent:
            # 节点没有走 LLM 流式输出（如 confirm_apply 的提交结果），补发一次 token
            logger.warning(
                f"本轮未收到 token 流，使用 fallback 一次性补发 | session_id={session_id}"
            )
            for message in reversed(values.get("messages") or []):
                if isinstance(message, AIMessage) and message.content:
                    yield sse_token(str(message.content))
                    break
                if (
                    isinstance(message, dict)
                    and message.get("type") == "ai"
                    and message.get("content")
                ):
                    yield sse_token(str(message["content"]))
                    break

        duration_ms: int = int((time.perf_counter() - started_at) * 1000)
        yield sse_done(duration_ms)

    except asyncio.CancelledError:
        logger.info(f"SSE 连接被取消 | session_id={session_id}")
        raise
    except Exception:
        logger.exception(f"AI 流式对话异常 | session_id={session_id}")
        yield sse_error("AI 服务暂时不可用，请稍后重试")


@router.post("/chat")
async def chat(
    data: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    发起一轮 AI 对话

    必须登录，user_id 从 token 解出，工具会用它做权限校验
    """
    session_id: str = data.session_id or uuid.uuid4().hex
    thread_id: str = build_thread_id(current_user.id, session_id)
    graph = get_graph()
    touch_thread(thread_id)

    async def event_generator():
        # SSE 生命周期长于请求依赖，这里单独创建并关闭会话
        db = SessionLocal()
        try:
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "db": db,
                }
            }
            payload = build_turn_input(data.message, current_user.id)
            async for item in _stream_events(
                graph, payload, config, request, session_id, query_text=data.message
            ):
                yield item
        finally:
            db.close()

    return EventSourceResponse(event_generator(), headers=SSE_HEADERS, ping=15)


@router.post("/confirm")
async def confirm(
    data: ConfirmRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """用户点击“确认提交”或“取消”后恢复暂停的图"""
    thread_id: str = build_thread_id(current_user.id, data.session_id)
    graph = get_graph()
    touch_thread(thread_id)

    async def event_generator():
        db = SessionLocal()
        try:
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "db": db,
                }
            }

            snapshot = await graph.aget_state(config)
            if not snapshot.values:
                yield sse_meta(data.session_id)
                yield sse_error("会话不存在或已过期，请重新开始对话")
                return

            resume = Command(resume={"confirmed": data.confirmed})
            async for item in _stream_events(
                graph, resume, config, request, data.session_id
            ):
                yield item
        finally:
            db.close()

    return EventSourceResponse(event_generator(), headers=SSE_HEADERS, ping=15)


@router.get("/health")
def health():
    """AI 配置自检：确认模型、向量库是否就绪（不返回密钥）"""
    status = get_ai_status()
    status["vector_store_ready"] = index_exists()
    return {"code": 200, "message": "请求成功", "data": status}
