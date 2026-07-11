"""
客服 Agent — 售后服务、订单查询、退货
"""

from models.schema import ChatState
from models.data import get_order, search_faq, return_process
import re


async def service_agent_node(state: ChatState) -> dict:
    """客服 Agent 节点 — 返回 dict"""
    user_input = state.user_input
    context_parts = []

    order_match = re.search(r'(ORD\d{3,})', user_input, re.IGNORECASE)
    if order_match:
        order_id = order_match.group(1).upper()
        order = get_order(order_id)
        if order:
            context_parts.append(
                f"订单 {order_id} 信息：\n"
                f"- 商品：{order['item']}\n"
                f"- 金额：\u00a5{order['price']}\n"
                f"- 状态：{order['status']}\n"
                f"- 下单日期：{order['date']}\n"
                f"- 物流：{order['logistics'] or '暂无'}\n"
                f"- 预计到达：{order['expected_arrival']}"
            )
        else:
            context_parts.append(f"未找到订单 {order_id}，请确认订单号。")

    if any(kw in user_input.lower() for kw in ["退货", "退款", "退"]):
        if order_match:
            result = return_process(order_match.group(1).upper())
            context_parts.append(result)
        else:
            faq_results = search_faq("退货")
            for q, a in faq_results:
                context_parts.append(f"FAQ - {q}：{a}")

    if any(kw in user_input.lower() for kw in ["物流", "快递", "什么时候到", "发货"]):
        context_parts.append("如需查询具体物流信息，请提供您的订单号（格式：ORD开头+数字）。")

    faq_keywords = ["发票", "保修", "支付", "配送", "发货时间", "退款时间"]
    for kw in faq_keywords:
        if kw in user_input.lower():
            faq_results = search_faq(kw)
            for q, a in faq_results:
                context_parts.append(f"FAQ - {q}：{a}")
            break

    if context_parts:
        response = "您好，我来帮您处理售后问题：\n\n" + "\n".join(context_parts) + "\n\n请问还有其他需要帮忙的吗？"
    else:
        response = (
            "您好！我是售后客服，请问有什么可以帮您？\n"
            "您可以：\n"
            "\u2022 查询订单状态（提供订单号）\n"
            "\u2022 了解退货/换货政策\n"
            "\u2022 查询物流信息\n"
            "\u2022 咨询发票问题"
        )

    return {"final_response": response, "current_agent": "service"}
