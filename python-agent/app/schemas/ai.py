"""
AI 对话接口的请求模型
作用: 约束消息长度与会话ID，避免超长输入与非法字符
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """发起一轮对话"""

    message: str = Field(min_length=1, max_length=2000, description="用户消息")
    session_id: str | None = Field(default=None, max_length=64, description="会话ID，不传则新建")


class ConfirmRequest(BaseModel):
    """二次确认结果"""

    session_id: str = Field(min_length=1, max_length=64, description="会话ID")
    confirmed: bool = Field(description="true-确认提交，false-取消")