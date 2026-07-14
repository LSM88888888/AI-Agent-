# 🖋 AI 多智能体客服/销售助手

> 基于 LangGraph + FastAPI + Streamlit 的多 Agent 系统  
> 模拟电子产品电商场景，支持售前咨询、售后服务、技术支持

---

## 📋 项目简介

本项目是一个 **Multi-Agent（多智能体）系统**，作为 FDE（前沿部署工程师）面试作品项目二，与项目一（RAG 知识库问答系统）互补：

| | 项目一 | 项目二 |
|---|---|---|
| **核心能力** | 理解（检索 + 生成） | 行动（编排 + 工具） |
| **技术栈** | LangChain + ChromaDB + Ollama | LangGraph + FastAPI + Streamlit |
| **架构** | 单一 RAG 链路 | 多 Agent 状态图 |
| **面试方向** | 检索、Embedding | Agent 编排、工具调用 |

---

## 🏗️ 系统架构

```
用户输入
    │
    ▼
┌──────────────┐
│  Supervisor  │  ← 意图识别（规则 / LLM）
│  (classify)  │
└──────┬───────┘
       │
       ├── sale    → ┌──────────────┐  售前咨询、产品推荐
       │             │  Sales Agent │  (ThinkPad / iPhone / MacBook...)
       │             └──────────────┘
       ├── service → ┌──────────────┐  订单查询、退货换货
       │             │Service Agent │  (ORD001 物流 / 退货政策 / 发票)
       │             └──────────────┘
       ├── tech    → ┌──────────────┐  故障诊断、使用帮助
       │             │  Tech Agent  │  (蓝屏 / WiFi / 卡顿 / 充电慢)
       │             └──────────────┘
       └── chat    → ┌──────────────┐  问候引导、闲聊
                     │  Chat Agent  │  (小墨 · 智能助手)
                     └──────────────┘
```

### 核心组件

- **Supervisor** — 意图识别 + 条件路由（LangGraph 条件边）
- **Sales Agent** — 调用 search_products 推荐商品
- **Service Agent** — 调用 get_order / return_process / search_faq
- **Tech Agent** — 调用 tech_diagnosis 提供解决方案
- **Chat Agent** — 问候/闲聊兜底

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- pip / venv

### 安装与运行

```bash
# 1. 进入项目目录
cd ai-multi-agent

# 2. 创建虚拟环境
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. 安装依赖
pip install langgraph fastapi uvicorn streamlit httpx pydantic python-dotenv

# 4. 启动后端 API
python main.py
# → http://localhost:8000
# → API 文档: http://localhost:8000/docs

# 5. 新终端启动前端（可选）
streamlit run streamlit_app.py
# → http://localhost:8501
```

### 无 API Key 运行

项目内置 Mock 模式，无需任何 API Key 即可完整运行。  
设置环境变量 `OPENAI_API_KEY` 后自动切换到 LLM 模式。

---

## 🎮 场景演示

| 场景 | 输入示例 | 处理 Agent |
|---|---|---|
| 💼 售前咨询 | "推荐一款办公笔记本" | Sales Agent |
| 💼 价格查询 | "iPhone 15 多少钱" | Sales Agent |
| 📦 订单查询 | "查一下订单 ORD001" | Service Agent |
| 📦 退货流程 | "ORD002 怎么退货" | Service Agent |
| 🔧 电脑蓝屏 | "电脑蓝屏了怎么办" | Tech Agent |
| 🔧 WiFi问题 | "WiFi 连不上" | Tech Agent |
| 🖋 闲聊问候 | "你好" / "你是谁" | Chat Agent |

---

## 📁 项目结构

```
ai-multi-agent/
├── main.py                 # FastAPI 入口（后端服务）
├── streamlit_app.py        # Streamlit 前端（聊天界面）
├── README.md               # 本文件
├── 项目规划.md              # 完整项目规划文档
├── 项目总结.md              # 项目总结与面试话术
├── config/
│   ├── settings.py         # 配置（API Key、端口等）
│   ├── prompts.py          # Prompt 模板（所有 LLM 提示词集中管理）
│   └── __init__.py
├── models/
│   ├── schema.py           # Pydantic 数据模型（ChatState / Message）
│   ├── data.py             # 模拟数据（商品/订单/FAQ/技术方案）
│   └── __init__.py
├── agents/
│   ├── supervisor.py       # 意图分类 + 路由判断
│   ├── sales_agent.py      # 销售 Agent
│   ├── service_agent.py    # 客服 Agent
│   ├── tech_agent.py       # 技术 Agent
│   ├── chat_agent.py       # 闲聊 Agent
│   └── __init__.py
├── graph/
│   ├── workflow.py         # LangGraph 状态图（节点 + 边 + 条件路由）
│   └── __init__.py
└── tests/
    ├── test_agents.py      # 测试脚本（13 个测试用例）
    └── __init__.py
```

---

## 🧪 测试

```bash
cd ai-multi-agent
python tests/test_agents.py
```

测试覆盖 4 类场景共 13 个用例：  
闲聊(2) + 销售(4) + 售后(4) + 技术(3)

---

## 🔧 扩展指南

### 添加新的 Agent

```python
# 1. 在 agents/ 下新建文件
# agents/logistics_agent.py
async def logistics_agent_node(state: ChatState) -> dict:
    return {"final_response": "...", "current_agent": "logistics"}

# 2. 在 graph/workflow.py 中添加节点
workflow.add_node("logistics_agent", logistics_agent_node)
workflow.add_edge("logistics_agent", END)

# 3. 在 agents/supervisor.py 中添加路由
routing = {
    # ... 已有规则
    "logistics": "logistics_agent",
}
```

### 切换真实 LLM

在项目目录下创建 `.env` 文件：

```env
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
```

重启后端即可。

---

## 📊 API 接口

### POST /chat

```json
// 请求
{ "message": "推荐一款办公笔记本" }

// 响应
{
  "reply": "根据您的需求，我为您推荐以下产品：\n\n• ThinkPad X1 Carbon — ¥9999\n  ...",
  "agent": "sales",
  "intent": "sale"
}
```

### GET /health

```json
{ "status": "ok" }
```

---

## 💡 面试亮点

1. **Multi-Agent 架构**：Supervisor + 专业 Agent 分层设计，职责清晰
2. **LangGraph 有状态图**：有向图编排、条件路由、状态共享
3. **可扩展性**：新增 Agent 只需加一个节点和一条边，零侵入
4. **Mock + LLM 双模式**：无 API Key 也能完整演示
5. **与项目一互补**：RAG（理解）+ Multi-Agent（行动），覆盖多类面试

---

## 📜 License

MIT
