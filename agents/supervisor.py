"""
主 Agent（Supervisor）— 意图识别 + 路由（V2）
V2 更新：扩展意图分类关键词，支持更多场景
"""

from config.settings import USE_REAL_LLM
from models.schema import ChatState


def _mock_classify(user_input: str) -> str:
    """无 LLM 时的简单规则分类（开发兜底）"""
    input_lower = user_input.lower()

    # 聊天/问候
    chat_keywords = [
        "你好", "嗨", "hello", "hi", "在吗", "你是谁", "help",
        "谢谢", "再见", "拜拜", "无聊", "聊天", "在不在", "干嘛",
    ]
    if any(kw in input_lower for kw in chat_keywords):
        return "chat"

    # 售后/客服
    service_keywords = [
        "订单", "退货", "换货", "退款", "物流", "快递", "投诉",
        "取消", "售后", "发票", "签收", "配送", "保修", "保障",
        "赔付", "价保", "积分", "会员", "验货", "以旧换新",
        "企业采购", "延保", "安装", "数据迁移", "隐私",
    ]
    if any(kw in input_lower for kw in service_keywords):
        return "service"

    # 技术问题
    tech_keywords = [
        "蓝屏", "死机", "卡顿", "wifi", "网络", "连不上", "驱动",
        "系统", "更新", "故障", "坏了", "不响", "充电", "不会",
        "怎么弄", "怎么搞", "怎么办", "解决", "维修", "修好",
        "开不了", "没声音", "发热", "闪退", "黑屏", "没信号",
        "耗电", "触控", "蓝牙", "指纹",
    ]
    if any(kw in input_lower for kw in tech_keywords):
        return "tech"

    # 销售/购物
    sale_keywords = [
        "推荐", "价格", "多少钱", "性价比", "对比", "哪个好",
        "买", "笔记本", "手机", "平板", "耳机", "配件",
        "办公", "游戏", "学生", "预算", "购物", "下单",
        "有货", "缺货", "库存", "品牌", "新款",
    ]
    if any(kw in input_lower for kw in sale_keywords):
        return "sale"

    # 兜底：默认路由到销售
    return "sale"


async def classify_intent(state: ChatState) -> dict:
    """意图分类节点 — 返回 dict，写入 intent 字段"""
    user_input = state.user_input
    if not user_input:
        intent = "chat"
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
