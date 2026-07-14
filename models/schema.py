"""
数据模型定义 — Pydantic 模型 + 模拟数据
V2 新增: 会话持久化支持
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    """单条消息"""
    role: str          # "user" | "assistant" | "system"
    content: str       # 消息内容
    agent: Optional[str] = None  # 处理该消息的 Agent 名称（可选）


class ChatState(BaseModel):
    """LangGraph 状态"""
    messages: list[Message] = Field(default_factory=list)
    current_agent: Optional[str] = None   # 当前处理 Agent
    intent: Optional[str] = None          # 识别到的意图: sale/service/tech/chat
    tool_results: list[str] = Field(default_factory=list)
    error: Optional[str] = None           # 错误信息
    user_input: str = ""                  # 用户当前输入（用于分类）
    final_response: str = ""              # 最终回复
    session_id: str = ""                  # 会话 ID（用于持久化）


class SessionRecord(BaseModel):
    """会话记录（用于持久化）"""
    session_id: str
    messages: List[dict] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
