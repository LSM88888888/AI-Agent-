"""
项目入口 — FastAPI 应用（V2）
V2 更新：
- 支持会话 ID（会话持久化）
- 集成 RAG 知识库
- 查看历史会话 API
"""

from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import API_HOST, API_PORT, PROJECT_NAME
from graph.workflow import run_agent
from session_store import create_session, append_message, get_session, list_sessions, delete_session
from models.schema import SessionRecord

app = FastAPI(title=f"{PROJECT_NAME} V2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== API 模型 ==========

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # 可选，不传则创建新会话


class ChatResponse(BaseModel):
    reply: str
    agent: Optional[str] = None
    intent: Optional[str] = None
    session_id: Optional[str] = None
    history_count: Optional[int] = None


class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    created_at: str
    updated_at: str
    preview: Optional[str] = None


# ========== API 路由 ==========

@app.get("/")
async def root():
    return {"message": f"{PROJECT_NAME} V2 is running", "version": "2.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理用户聊天消息（V2 — 支持会话持久化）

    - 输入: {"message": "推荐一款笔记本", "session_id": "abc123"}
    - 输出: {"reply": "...", "agent": "sales", "intent": "sale", "session_id": "abc123"}
    """
    if not request.message.strip():
        return ChatResponse(reply="请输入您的问题。", session_id=request.session_id)

    # 会话管理：创建新会话或复用已有会话
    session_id = request.session_id or create_session()

    # 保存用户消息
    append_message(session_id, "user", request.message.strip())

    # 运行 Agent
    result = await run_agent(request.message.strip(), session_id)

    # 保存 AI 回复
    reply = result.final_response or "抱歉，我暂时无法处理您的问题，请联系人工客服。"
    append_message(session_id, "assistant", reply, agent=result.current_agent)

    # 获取历史消息数量
    session = get_session(session_id)
    history_count = len(session.messages) if session else 0

    return ChatResponse(
        reply=reply,
        agent=result.current_agent,
        intent=result.intent,
        session_id=session_id,
        history_count=history_count,
    )


@app.get("/sessions", response_model=list[SessionInfo])
async def get_sessions(limit: int = Query(20, ge=1, le=100)):
    """获取会话列表（按更新时间倒序）"""
    sessions = list_sessions(limit)
    result = []
    for s in sessions:
        preview = ""
        if s.messages:
            last_msg = s.messages[-1]
            preview = last_msg.get("content", "")[:50]
        result.append(SessionInfo(
            session_id=s.session_id,
            message_count=len(s.messages),
            created_at=s.created_at,
            updated_at=s.updated_at,
            preview=preview,
        ))
    return result


@app.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    """获取指定会话的完整历史"""
    session = get_session(session_id)
    if not session:
        return {"error": "会话不存在"}, 404
    return session.model_dump()


@app.delete("/sessions/{session_id}")
async def remove_session(session_id: str):
    """删除指定会话"""
    ok = delete_session(session_id)
    if not ok:
        return {"error": "会话不存在"}, 404
    return {"message": "会话已删除"}


# ========== 启动入口 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
