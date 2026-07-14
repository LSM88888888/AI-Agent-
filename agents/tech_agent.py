"""
技术 Agent — 技术支持、故障诊断（V2）
V2 更新：
- 接入 20+ 技术方案
- 接入 RAG 知识库补充信息
- 智能匹配更多技术关键词
"""

from models.schema import ChatState
from models.data import tech_diagnosis, list_all_issues
from kb_utils import get_kb


async def tech_agent_node(state: ChatState) -> dict:
    """技术 Agent 节点 — 返回 dict"""
    user_input = state.user_input

    # V2: 扩展关键词映射（覆盖 20+ 问题）
    tech_issues = {
        # 电脑
        "蓝屏": "电脑蓝屏",
        "死机": "电脑蓝屏",
        "重启": "电脑蓝屏",
        "系统崩溃": "电脑蓝屏",
        # 网络
        "wifi": "wifi连不上",
        "网络": "wifi连不上",
        "连不上": "wifi连不上",
        "断网": "wifi连不上",
        "上不了网": "wifi连不上",
        # 手机
        "卡顿": "手机卡顿",
        "慢": "手机卡顿",
        "反应慢": "手机卡顿",
        "卡": "手机卡顿",
        # 充电
        "充电慢": "充电缓慢",
        "充不进": "充电缓慢",
        "充不了电": "充电缓慢",
        "充电快慢": "充电缓慢",
        # 屏幕
        "闪烁": "屏幕闪烁",
        "花屏": "屏幕闪烁",
        "闪屏": "屏幕闪烁",
        # 音频
        "没声音": "耳机没声音",
        "没声": "耳机没声音",
        "无声": "耳机没声音",
        "杂音": "声音杂音",
        "破音": "声音杂音",
        # 电池
        "耗电": "电池耗电快",
        "不耐用": "电池耗电快",
        "掉电": "电池耗电快",
        # 摄像头
        "模糊": "摄像头模糊",
        "不清晰": "摄像头模糊",
        # 开机
        "开不了机": "无法开机",
        "不能开机": "无法开机",
        "不开机": "无法开机",
        # 触屏
        "触摸屏": "触摸屏失灵",
        "触控": "触摸屏失灵",
        "点不了": "触摸屏失灵",
        # 系统
        "更新失败": "系统更新失败",
        "升级失败": "系统更新失败",
        # 应用
        "闪退": "应用闪退",
        "打不开": "应用闪退",
        # 蓝牙
        "蓝牙连不上": "蓝牙连接不上",
        "蓝牙搜索不到": "蓝牙连接不上",
        # 存储
        "内存不足": "存储空间不足",
        "空间不够": "存储空间不足",
        "存储不够": "存储空间不足",
        # 指纹
        "指纹": "指纹识别失灵",
        # 信号
        "信号差": "网络信号差",
        "没信号": "网络信号差",
        # 相机
        "相机黑屏": "相机黑屏",
        "拍不了": "相机黑屏",
        # 键盘
        "键盘": "键盘失灵",
        "按键": "键盘失灵",
        # 发热
        "发热": "发热严重",
        "烫": "发热严重",
    }

    matched_issue = None
    for keyword, issue in tech_issues.items():
        if keyword in user_input.lower():
            matched_issue = issue
            break

    if matched_issue:
        solution = tech_diagnosis(matched_issue)
    else:
        # 尝试更广泛的匹配
        all_issues = list_all_issues()
        for issue in all_issues:
            if any(kw in user_input.lower() for kw in [issue[:2], issue]):
                solution = tech_diagnosis(issue)
                break
        else:
            solution = tech_diagnosis(user_input)

    # RAG 补充
    kb = get_kb()
    rag_results = kb.search(user_input, k=2)
    rag_text = ""
    for content, meta, score in rag_results:
        if meta.get("type") == "document":
            rag_text = f"\n\n\U0001f4d6 **知识库参考：**\n{content[:200]}"

    response = (
        f"我来帮您排查技术问题：\n\n{solution}{rag_text}\n\n"
        "如果以上方法未能解决您的问题，请联系人工技术支持。\n"
        "电话：400-xxx-xxxx\n邮箱：support@example.com"
    )

    return {"final_response": response, "current_agent": "tech"}
