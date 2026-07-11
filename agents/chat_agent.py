"""
聊天 Agent — 闲聊/问候/默认
"""

from models.schema import ChatState


async def chat_agent_node(state: ChatState) -> dict:
    """闲聊/默认 Agent 节点 — 返回 dict"""
    user_input = state.user_input

    greetings = {
        "你好": "你好呀！我是「小墨」，您的智能购物助手 🖋\n请问有什么可以帮您的？我可以：\n\u2022 \U0001f4bc 推荐产品 \u2728\n\u2022 \U0001f4e6 查询订单 \U0001f4cb\n\u2022 \U0001f527 技术帮助 \U0001f6e0\ufe0f",
        "嗨": "嗨！\U0001f44b 有什么可以帮您的吗？",
        "你是谁": "我是「小墨」，您的智能购物助手！我可以帮您推荐产品、查询订单、解决技术问题～",
        "谢谢": "不客气！有需要随时找我 \U0001f60a",
        "再见": "再见！祝您生活愉快 \U0001f389",
        "拜拜": "拜拜～下次见！",
    }

    response = None
    for key, reply in greetings.items():
        if key in user_input.lower():
            response = reply
            break

    if response is None:
        response = (
            "你好！我是「小墨」，您的智能购物助手。\n"
            "请问有什么可以帮您？比如：\n\n"
            "\U0001f4bc **购物咨询** \u2014 \u300c推荐一款办公笔记本\u300d\n"
            "\U0001f4e6 **订单查询** \u2014 \u300c我的订单 ORD001 到哪了\u300d\n"
            "\U0001f527 **技术支持** \u2014 \u300c电脑蓝屏怎么办\u300d"
        )

    return {"final_response": response, "current_agent": "chat"}
