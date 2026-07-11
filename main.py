"""
项目入口 — FastAPI 应用
"""

from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import API_HOST, API_PORT, PROJECT_NAME
from graph.workflow import run_agent

app = FastAPI(title=PROJECT_NAME)

# CORS（允许前端跨域访问）
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


class ChatResponse(BaseModel):
    reply: str
    agent: Optional[str] = None
    intent: Optional[str] = None


# ========== API 路由 ==========

@app.get("/")
async def root():
    return {"message": f"{PROJECT_NAME} API is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理用户聊天消息

    - 输入: {"message": "推荐一款笔记本"}
    - 输出: {"reply": "...", "agent": "sales", "intent": "sale"}
    """
    if not request.message.strip():
        return ChatResponse(reply="请输入您的问题。", agent=None, intent=None)

    result = await run_agent(request.message.strip())

    return ChatResponse(
        reply=result.final_response or "抱歉，我暂时无法处理您的问题，请联系人工客服。",
        agent=result.current_agent,
        intent=result.intent,
    )


# ========== 启动入口 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
