"""
销售 Agent — 售前咨询、产品推荐
"""

from models.schema import ChatState
from models.data import search_products

import re


async def sales_agent_node(state: ChatState) -> dict:
    """销售 Agent 节点 — 返回 dict 让 LangGraph 自动更新状态"""
    user_input = state.user_input

    sale_keywords = ["办公", "游戏", "学生", "旗舰", "中端", "降噪", "充电"]
    matched_category = None
    for kw in sale_keywords:
        if kw in user_input.lower():
            matched_category = kw
            break

    if matched_category == "办公":
        results = search_products(scenario="办公")
    elif matched_category == "游戏":
        results = search_products(scenario="游戏")
    elif matched_category == "学生":
        results = search_products(scenario="学生")
    elif matched_category in ("旗舰", "中端"):
        phone_results = search_products(category="手机")
        results = [p for p in phone_results if matched_category == p.get("scenario")]
    elif matched_category == "降噪":
        results = search_products(scenario="降噪")
    elif matched_category == "充电":
        results = search_products(scenario="充电")
    else:
        for cat in ("笔记本", "手机", "平板", "耳机", "配件"):
            if cat in user_input.lower():
                results = search_products(category=cat)
                break
        else:
            results = list(search_products())

    price_match = re.search(r'(\d+)\s*元', user_input)
    if price_match:
        budget = int(price_match.group(1))
        results = [p for p in results if p["price"] <= budget * 1.2]

    if results:
        response = (
            f"根据您的需求，我为您推荐以下产品：\n\n"
            + "\n".join(
                f'\u2022 **{p["name"]}** \u2014 \u00a5{p["price"]}\n  {p["desc"]}'
                for p in results[:3]
            )
            + "\n\n请问您对哪一款感兴趣？我可以为您提供更详细的信息。"
        )
    else:
        response = (
            "您好！请问您有什么购物需求？我可以帮您推荐适合的产品。\n"
            "比如您是在找笔记本、手机、还是其他电子产品？预算大概是多少？"
        )

    return {"final_response": response, "current_agent": "sales"}
