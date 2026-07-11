# AI 多智能体客服/销售助手

## 项目概述

基于 **LangGraph + FastAPI + Streamlit** 的多智能体（Multi-Agent）系统，模拟电子产品电商场景，支持售前咨询、售后服务、技术支持三大业务场景。

**项目特点：**
- 4 个专业 Agent（销售/客服/技术/闲聊）+ 1 个 Supervisor 调度层
- LangGraph 有状态图编排，条件路由自动分流
- 可扩展架构——新增 Agent 只需加一个节点和一条边
- Mock + LLM 双模式，无 API Key 也可运行

---

## 技术栈

| 组件 | 技术 |
|------|------|
| AI 编排 | LangGraph |
| 状态管理 | Pydantic v2 |
| 后端 API | FastAPI |
| 前端 UI | Streamlit |
| 数据存储 | 内存模拟数据（ChromaDB 就绪） |
| Python 版本 | 3.9+ |

---

## 系统架构

```
用户输入
    │
    ▼
┌──────────────┐
│  Supervisor  │  ← 意图识别
│  (classify)  │
└──────┬───────┘
       │
       ├── sale    → ┌──────────────┐
       │             │  Sales Agent │ 售前咨询、产品推荐
       │             └──────────────┘
       ├── service → ┌──────────────┐
       │             │Service Agent │ 订单查询、退货/退款
       │             └──────────────┘
       ├── tech    → ┌──────────────┐
       │             │  Tech Agent  │ 故障诊断、使用问题
       │             └──────────────┘
       └── chat    → ┌──────────────┐
                     │  Chat Agent  │ 问候、闲聊
                     └──────────────┘
```

---

## 快速启动

### 1. 安装依赖

```bash
cd projects/ai-multi-agent-project
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. 启动后端 API

```bash
python main.py
# 服务运行在 http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 3. 启动前端界面（新终端）

```bash
streamlit run streamlit_app.py
# 浏览器打开 http://localhost:8501
```

---

## API 接口

### POST /chat
处理用户消息并返回回复。

**请求体：**
```json
{"message": "推荐一款办公笔记本"}
```

**响应：**
```json
{
  "reply": "根据您的需求，我为您推荐以下产品：\n\n...",
  "agent": "sales",
  "intent": "sale"
}
```

### GET /health
健康检查。

---

## 场景测试

| 场景 | 示例输入 | 处理 Agent |
|------|---------|-----------|
| 售前咨询 | "推荐一款办公笔记本" | Sales Agent |
| 订单查询 | "我的 ORD001 到哪了" | Service Agent |
| 退货流程 | "ORD002 怎么退货" | Service Agent |
| 技术诊断 | "电脑蓝屏怎么办" | Tech Agent |
| 闲聊问候 | "你好" / "你是谁" | Chat Agent |

---

## 项目结构

```
ai-multi-agent-project/
├── main.py                 # FastAPI 入口
├── streamlit_app.py        # Streamlit 前端
├── requirements.txt        # 依赖清单
├── config/
│   ├── settings.py         # 配置（API Key、模型选择）
│   └── prompts.py          # Prompt 模板（集中管理）
├── models/
│   ├── schema.py           # Pydantic 数据模型
│   └── data.py             # 模拟数据 + 工具函数
├── agents/
│   ├── supervisor.py       # 意图分类 + 路由
│   ├── sales_agent.py      # 销售 Agent
│   ├── service_agent.py    # 客服 Agent
│   ├── tech_agent.py       # 技术 Agent
│   └── chat_agent.py       # 闲聊 Agent
├── graph/
│   └── workflow.py         # LangGraph 状态图定义
└── tests/
    └── test_agents.py      # 测试脚本
```

---

## 扩展指南

### 添加新的 Agent

1. 在 `agents/` 下创建新文件
2. 在 `graph/workflow.py` 中添加节点和边
3. 在 `agents/supervisor.py` 中添加路由规则

示例——新增"物流 Agent"：

```python
# graph/workflow.py
workflow.add_node("logistics_agent", logistics_agent_node)
workflow.add_edge("logistics_agent", END)

# supervisor.py 的路由映射
routing = {
    # ... 已有规则
    "logistics": "logistics_agent",
}
```

### 对接真实 LLM

在 `.env` 文件中设置 `OPENAI_API_KEY`，系统自动切换到 LLM 模式。

---

## 面试亮点

- **Multi-Agent 架构**：Supervisor + 专业 Agent 的分层设计
- **LangGraph 状态图**：有向图编排、条件路由、状态共享
- **可扩展性**：新增 Agent 只需加一个节点
- **Mock 兜底**：无 API Key 也可完整演示
- **双模式**：规则分类（开发）→ LLM 分类（生产）无缝切换
