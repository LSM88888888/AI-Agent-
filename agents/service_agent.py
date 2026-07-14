"""
客服 Agent — 售后服务、订单查询、退货（V2）
V2 更新：
- 接入 30+ 订单数据
- 接入 20+ FAQ
- 接入 RAG 知识库补充信息
"""

from models.schema import ChatState
from models.data import get_order, search_faq, return_process, search_orders_by_status
from kb_utils import get_kb
import re


async def service_agent_node(state: ChatState) -> dict:
    """客服 Agent 节点 — 返回 dict"""
    user_input = state.user_input
    context_parts = []

    # V2：按状态查询订单
    status_keywords = {
        "已发货": ["已发货", "发货了", "在途", "快递"],
        "待发货": ["待发货", "未发货", "还没发"],
        "已完成": ["已完成", "到了", "收到"],
        "已取消": ["已取消", "取消了"],
    }
    for status, keywords in status_keywords.items():
        if any(kw in user_input.lower() for kw in keywords):
            status_orders = search_orders_by_status(status)
            if status_orders:
                context_parts.append(
                    f"您有 {len(status_orders)} 个【{status}】订单：\n"
                    + "\n".join(
                        f"  \u2022 **{o['item']}** \u2014 \u00a5{o['price']:,} (订单: {o['order_id']})"
                        for o in status_orders[:5]
                    )
                    + ("\n  ...更多订单可提供具体订单号查询。" if len(status_orders) > 5 else "")
                )

    # V2：按数量查询
    order_count_match = re.search(r'(最近|近)\s*(\d+)\s*(个|笔|条)?\s*订单', user_input.lower())
    if order_count_match:
        count = int(order_count_match.group(2))
        context_parts.append(f"正在查询最近 {count} 笔订单...（请提供具体订单号获取详细信息）")

    # 按订单号查询
    order_match = re.search(r'(ORD\d{3,})', user_input, re.IGNORECASE)
    if order_match:
        order_id = order_match.group(1).upper()
        order = get_order(order_id)
        if order:
            context_parts.append(
                f"订单 {order_id} 信息：\n"
                f"  \u2022 商品：{order['item']}\n"
                f"  \u2022 金额：\u00a5{order['price']:,}\n"
                f"  \u2022 状态：{order['status']}\n"
                f"  \u2022 下单日期：{order['date']}\n"
                f"  \u2022 物流：{order['logistics'] or '暂无'}\n"
                f"  \u2022 预计到达：{order['expected_arrival']}"
            )
        else:
            context_parts.append(f"未找到订单 {order_id}，请确认订单号是否正确。")

    # 退货流程
    if any(kw in user_input.lower() for kw in ["退货", "退款", "退"]):
        if order_match:
            result = return_process(order_match.group(1).upper())
            context_parts.append(result)
        else:
            faq_results = search_faq("退货")
            for q, a in faq_results:
                context_parts.append(f"FAQ \u2014 {q}：{a}")

    # FAQ 匹配
    faq_keywords = [
        "发票", "保修", "支付", "配送", "发货时间", "退款时间",
        "换货", "价格", "积分", "会员", "验货", "物流查询",
        "修改地址", "取消订单", "缺货", "以旧换新", "企业采购",
        "延保", "安装", "数据迁移", "隐私",
    ]
    for kw in faq_keywords:
        if kw in user_input.lower():
            faq_results = search_faq(kw)
            for q, a in faq_results:
                context_parts.append(f"FAQ \u2014 {q}：{a}")
            break

    # RAG 补充
    kb = get_kb()
    rag_results = kb.search(user_input, k=2)
    rag_added = False
    for content, meta, score in rag_results:
        if meta.get("type") == "document" and not rag_added:
            context_parts.append(f"\U0001f4d6 相关信息：{content[:150]}...")
            rag_added = True

    if context_parts:
        response = "您好，我来帮您处理售后问题：\n\n" + "\n\n".join(context_parts) + "\n\n请问还有其他需要帮忙的吗？"
    else:
        response = (
            "您好！我是售后客服，请问有什么可以帮您？\n"
            "您可以：\n"
            "\u2022 查询订单状态（提供订单号，如 ORD001）\n"
            "\u2022 查看订单列表（告诉我状态或数量）\n"
            "\u2022 了解退货/换货政策\n"
            "\u2022 查询物流信息\n"
            "\u2022 咨询发票/价格/保修等问题"
        )

    return {"final_response": response, "current_agent": "service"}
