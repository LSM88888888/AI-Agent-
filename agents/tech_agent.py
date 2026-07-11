"""
技术 Agent — 技术支持、故障诊断
"""

from models.schema import ChatState
from models.data import tech_diagnosis


async def tech_agent_node(state: ChatState) -> dict:
    """技术 Agent 节点 — 返回 dict"""
    user_input = state.user_input

    tech_issues = {
        "蓝屏": "电脑蓝屏",
        "死机": "电脑蓝屏",
        "wifi": "wifi连不上",
        "网络": "wifi连不上",
        "连不上": "wifi连不上",
        "卡顿": "手机卡顿",
        "慢": "手机卡顿",
        "充电慢": "充电缓慢",
        "充不进": "充电缓慢",
    }

    matched_issue = None
    for keyword, issue in tech_issues.items():
        if keyword in user_input.lower():
            matched_issue = issue
            break

    if matched_issue:
        solution = tech_diagnosis(matched_issue)
    else:
        solution = tech_diagnosis(user_input)

    response = (
        f"我来帮您排查技术问题：\n\n{solution}\n\n"
        "如果以上方法未能解决您的问题，请联系人工技术支持。\n"
        "电话：400-xxx-xxxx\n邮箱：support@example.com"
    )

    return {"final_response": response, "current_agent": "tech"}
