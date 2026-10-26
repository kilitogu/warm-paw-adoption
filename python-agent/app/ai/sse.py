"""
SSE 事件封装
作用: 统一事件名与 data 序列化，避免每个接口手写字符串
"""
import json
from typing import Any


def _pack(event: str, payload: dict[str, Any]) -> dict:
    """EventSourceResponse 接受的字典格式"""
    return {
        "event": event,
        "data": json.dumps(payload, ensure_ascii=False),
    }


def sse_meta(session_id: str) -> dict:
    """会话开始"""
    return _pack("meta", {"session_id": session_id})


def sse_intent(intent: str) -> dict:
    """意图识别完成"""
    return _pack("intent", {"intent": intent})


def sse_retrieval(query: str, sources: list[dict]) -> dict:
    """RAG 检索完成"""
    return _pack("retrieval", {"query": query, "sources": sources})


def sse_tool_start(tool: str, args: dict) -> dict:
    """工具调用开始"""
    return _pack("tool_start", {"tool": tool, "args": args})


def sse_tool_end(tool: str, result_summary: str) -> dict:
    """工具调用结束"""
    return _pack("tool_end", {"tool": tool, "result_summary": result_summary})


def sse_token(content: str) -> dict:
    """LLM 逐字输出"""
    return _pack("token", {"content": content})


def sse_confirm(payload: dict) -> dict:
    """需要用户二次确认"""
    return _pack("confirm", payload)


def sse_done(duration_ms: int) -> dict:
    """本轮结束"""
    return _pack("done", {"duration_ms": duration_ms})


def sse_error(message: str, code: int = 500) -> dict:
    """异常"""
    return _pack("error", {"message": message, "code": code})