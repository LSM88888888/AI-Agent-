"""
主 Agent（Supervisor）— 意图识别 + 路由
"""

from config.settings import USE_REAL_LLM
from config.prompts import INTENT_CLASSIFIER_PROMPT
from models.schema import ChatState


def _mock_classify(user_input: str) -> str:
    """无 LLM 时的简单规则分类（开发兜底）"""
    input_lower = user_input.lower()

    chat_keywords = ["你好", "嗨", "hello", "hi", "在吗", "你是谁", "help", "谢谢", "再见", "拜拜"]
    if any(kw in input_lower for kw in chat_keywords):
        return "chat"

    service_keywords = ["订单", "退货", "换货", "退款", "物流", "快递", "投诉",
                        "取消", "售后", "发票", "签收", "配送"]
    if any(kw in input_lower for kw in service_keywords):
        return "service"

    tech_keywords = ["蓝屏", "死机", "卡顿", "wifi", "网络", "连不上", "驱动",
                     "系统", "更新", "故障", "问题", "坏了", "不响", "充电"]
    if any(kw in input_lower for kw in tech_keywords):
        return "tech"

    sale_keywords = ["推荐", "价格", "多少钱", "性价比", "对比", "哪个好",
                     "买", "笔记本", "手机", "平板", "耳机", "配件",
                     "办公", "游戏", "学生", "预算"]
    if any(kw in input_lower for kw in sale_keywords):
        return "sale"

    return "sale"


async def classify_intent(state: ChatState) -> dict:
    """意图分类节点 — 返回 dict，写入 intent 字段"""
    user_input = state.user_input
    if not user_input:
        intent = "chat"
    elif USE_REAL_LLM:
        intent = _mock_classify(user_input)
    else:
        intent = _mock_classify(user_input)

    return {"intent": intent}


def route_decision(state: ChatState) -> str:
    """路由判断 — 返回下一个节点的名称"""
    intent = state.intent or "chat"
    routing = {
        "sale": "sales_agent",
        "service": "service_agent",
        "tech": "tech_agent",
        "chat": "chat_agent",
    }
    return routing.get(intent, "chat_agent")
