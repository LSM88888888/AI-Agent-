"""
销售 Agent — 售前咨询、产品推荐（V2）
V2 更新：
- 使用复用项目一 products.json 的新数据接口
- 支持分类/品牌/价格/关键词搜索
- 引入 RAG 知识库补充信息
"""

from models.schema import ChatState
from models.data import search_products
from kb_utils import get_kb

import re


async def sales_agent_node(state: ChatState) -> dict:
    """销售 Agent 节点 — 返回 dict 让 LangGraph 自动更新状态"""
    user_input = state.user_input

    # V2 增强检索：多维度搜索
    results = []

    # 优先按分类搜索
    categories = ["笔记本", "手机", "平板", "耳机", "配件", "智能穿戴"]
    for cat in categories:
        if cat in user_input.lower():
            results = search_products(category=cat)
            break

    # 按品牌搜索
    brands = ["联想", "Apple", "华硕", "华为", "小米", "戴尔", "三星", "Sony", "Bose", "荣耀", "红米"]
    matched_brand = None
    for brand in brands:
        if brand in user_input.lower():
            matched_brand = brand
            results = search_products(brand=brand)
            break

    # 按关键词搜索
    if not results:
        results = search_products(keyword=user_input)

    # 按标签搜索
    if not results:
        tags = ["办公", "游戏", "学生", "旗舰", "轻薄", "降噪", "性价比"]
        for tag in tags:
            if tag in user_input.lower():
                results = search_products(tag=tag)
                break

    # 按预算过滤
    price_match = re.search(r'(\d+)\s*元', user_input)
    if price_match:
        budget = int(price_match.group(1))
        results = [p for p in results if p["price"] <= budget * 1.2]

    # RAG 补充：搜索知识库获取更多信息
    kb = get_kb()
    rag_results = kb.search(user_input, k=2)

    if results:
        lines = []
        for p in results[:3]:
            stock_str = "\U0001f7e2 库存{}枚".format(p["stock"]) if p["stock"] > 0 else "\u274c 缺货"
            line = "\u2022 **{}** \u2014 \u00a5{:,} ({})\n  {}".format(
                p["name"], p["price"], stock_str, p["desc"][:80]
            )
            lines.append(line)
        response = "根据您的需求，我为您推荐以下产品：\n\n" + "\n".join(lines)

        # 如果 RAG 返回了相关信息，附加
        if rag_results:
            response += "\n\n\U0001f4d6 **扩展信息：**\n"
            for content, meta, score in rag_results[:2]:
                if meta.get("type") == "document":
                    response += f"\n  \u2022 {content[:100]}..."

        response += "\n\n请问您对哪一款感兴趣？我可以为您提供更详细的信息。"
    else:
        response = (
            "您好！请问您有什么购物需求？我可以帮您推荐适合的产品。\n"
            "比如您是在找笔记本、手机、还是其他电子产品？预算大概是多少？"
        )

    return {"final_response": response, "current_agent": "sales"}
