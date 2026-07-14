"""
LangGraph 状态图定义（V2）
V2 更新：
- 支持 session_id 传入
- Agent 调用 RAG 知识库
"""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from models.schema import ChatState
from models.schema import Message
from agents.supervisor import classify_intent, route_decision
from agents.sales_agent import sales_agent_node
from agents.service_agent import service_agent_node
from agents.tech_agent import tech_agent_node
from agents.chat_agent import chat_agent_node


def build_graph() -> CompiledStateGraph:
    """构建 Multi-Agent 工作流图"""

    # 1. 创建图
    workflow = StateGraph(ChatState)

    # 2. 添加节点
    workflow.add_node("classify", classify_intent)
    workflow.add_node("sales_agent", sales_agent_node)
    workflow.add_node("service_agent", service_agent_node)
    workflow.add_node("tech_agent", tech_agent_node)
    workflow.add_node("chat_agent", chat_agent_node)

    # 3. 设置入口
    workflow.set_entry_point("classify")

    # 4. 条件边
    workflow.add_conditional_edges(
        "classify",
        route_decision,
        {
            "sales_agent": "sales_agent",
            "service_agent": "service_agent",
            "tech_agent": "tech_agent",
            "chat_agent": "chat_agent",
        },
    )

    # 5. 所有 Agent 完成后结束
    workflow.add_edge("sales_agent", END)
    workflow.add_edge("service_agent", END)
    workflow.add_edge("tech_agent", END)
    workflow.add_edge("chat_agent", END)

    # 6. 编译
    return workflow.compile()


# 全局单例
agent_graph = build_graph()


async def run_agent(user_input: str, session_id: str = "") -> ChatState:
    """运行 Agent，返回最终状态"""
    initial_state = ChatState(
        messages=[Message(role="user", content=user_input)],
        user_input=user_input,
        session_id=session_id,
    )
    result = await agent_graph.ainvoke(initial_state)
    if isinstance(result, dict):
        return ChatState(**result)
    return result
