"""
模拟数据 — 商品、订单、FAQ、技术知识库
"""

from typing import Optional, List

# ========== 商品 ==========
products = {
    "笔记本-办公": {
        "name": "ThinkPad X1 Carbon",
        "category": "笔记本",
        "scenario": "办公",
        "price": 9999,
        "stock": 50,
        "desc": "14寸轻薄商务本，1.1kg重量，Intel i7-1365U",
    },
    "笔记本-游戏": {
        "name": "ROG 枪神6",
        "category": "笔记本",
        "scenario": "游戏",
        "price": 12999,
        "stock": 20,
        "desc": "16寸高性能游戏本，RTX 4070独显，165Hz高刷屏",
    },
    "笔记本-学生": {
        "name": "MacBook Air M3",
        "category": "笔记本",
        "scenario": "学生",
        "price": 8999,
        "stock": 80,
        "desc": "13.6寸，M3芯片，18小时续航，适合学生和轻度办公",
    },
    "手机-旗舰": {
        "name": "iPhone 15 Pro",
        "category": "手机",
        "scenario": "旗舰",
        "price": 8999,
        "stock": 100,
        "desc": "A17 Pro芯片，钛金属外壳，4800万像素三摄",
    },
    "手机-中端": {
        "name": "小米14",
        "category": "手机",
        "scenario": "中端",
        "price": 3999,
        "stock": 200,
        "desc": "徕卡光学三摄，骁龙8 Gen3，5000mAh大电池",
    },
    "平板": {
        "name": "iPad Air M2",
        "category": "平板",
        "scenario": "通用",
        "price": 4799,
        "stock": 30,
        "desc": "11英寸 Liquid Retina 屏，M2芯片，支持Apple Pencil Pro",
    },
    "耳机-降噪": {
        "name": "AirPods Pro 2",
        "category": "耳机",
        "scenario": "降噪",
        "price": 1899,
        "stock": 150,
        "desc": "自适应降噪，H2芯片，USB-C充电，最长6小时续航",
    },
    "配件-充电": {
        "name": "Anker 65W GaN充电器",
        "category": "配件",
        "scenario": "充电",
        "price": 299,
        "stock": 500,
        "desc": "65W氮化镓，双C口，支持PD快充，兼容笔记本和手机",
    },
}


def search_products(**kwargs) -> List[dict]:
    """按条件搜索商品"""
    result = list(products.values())
    for key, val in kwargs.items():
        if key == "category":
            result = [p for p in result if p["category"] == val]
        elif key == "scenario":
            result = [p for p in result if p["scenario"] == val]
        elif key == "max_price":
            result = [p for p in result if p["price"] <= val]
        elif key == "min_price":
            result = [p for p in result if p["price"] >= val]
        elif key == "keyword":
            result = [
                p for p in result
                if val.lower() in p["name"].lower()
                or val.lower() in p["desc"].lower()
            ]
    return result


# ========== 订单 ==========
orders = {
    "ORD001": {
        "status": "已发货",
        "item": "ThinkPad X1 Carbon",
        "price": 9999,
        "date": "2026-07-08",
        "logistics": "顺丰 SF1234567890",
        "expected_arrival": "2026-07-12",
    },
    "ORD002": {
        "status": "待发货",
        "item": "iPhone 15 Pro",
        "price": 8999,
        "date": "2026-07-10",
        "logistics": None,
        "expected_arrival": "预计2026-07-14前送达",
    },
    "ORD003": {
        "status": "已完成",
        "item": "AirPods Pro 2",
        "price": 1899,
        "date": "2026-07-01",
        "logistics": "顺丰 SF9876543210",
        "expected_arrival": "2026-07-04",
    },
    "ORD004": {
        "status": "已取消",
        "item": "小米14",
        "price": 3999,
        "date": "2026-07-05",
        "logistics": None,
        "expected_arrival": "已取消",
    },
}


def get_order(order_id: str) -> Optional[dict]:
    """根据订单号查询订单"""
    return orders.get(order_id.upper())


# ========== 售后/FAQ ==========
faq = {
    "退货政策": "签收后7天内可无理由退货，需保持商品完好、配件齐全、包装完整。退回运费由买家承担（商品质量问题除外）。",
    "换货政策": "签收后15天内，如出现非人为质量问题，可免费换货。",
    "保修期限": "所有电子产品享有一年官方保修。保修期内非人为损坏免费维修。",
    "发货时间": "工作日6:00前下单，当天发货；6:00后下单，次日发货。节假日顺延。",
    "退款时间": "退货审核通过后，退款将在3-5个工作日内原路返回。",
    "配送范围": "全国范围（港澳台地区除外）均可配送，部分偏远地区时效可能延长。",
    "支付方式": "支持支付宝、微信支付、银行卡、花呗分期（3/6/12期）。",
    "发票说明": "支持电子发票和纸质发票，下单时选择即可。电子发票将在发货后发送到邮箱。",
}


def search_faq(keyword: str) -> List[tuple]:
    """搜索FAQ，返回匹配的 (问题, 答案) 列表"""
    results = []
    for question, answer in faq.items():
        if keyword.lower() in question.lower() or keyword.lower() in answer.lower():
            results.append((question, answer))
    if not results:
        return list(faq.items())[:3]
    return results


def return_process(order_id: str) -> str:
    """退货流程说明"""
    order = get_order(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"
    if order["status"] in ("已取消",):
        return f"订单 {order_id} 已取消，无法发起退货。"
    if order["status"] == "已完成":
        return (
            f"订单 {order_id}（{order['item']}）已完成，"
            f"仍在7天退货期内。如需退货请按以下步骤操作：\n"
            f"1. 联系客服申请退货\n"
            f"2. 将商品寄回至：XX市XX区XX路X号\n"
            f"3. 审核通过后3-5工作日退款"
        )
    # 待发货/已发货
    return (
        f"订单 {order_id}（{order['item']}）当前状态为【{order['status']}】，"
        f"建议先去订单页面取消订单后再重新下单。"
        f"如需协助请联系人工客服。"
    )


# ========== 技术支持 ==========
tech_tips = {
    "电脑蓝屏": [
        "1. 重启电脑，看是否能正常进入系统",
        "2. 如果重启后仍然蓝屏，尝试进入安全模式",
        "3. 检查最近是否安装了新硬件或软件，尝试卸载",
        "4. 运行内存诊断：搜索'Windows 内存诊断' -> 立即重启检查",
        "5. 如果以上方法无效，可能是硬件故障，建议送修",
    ],
    "wifi连不上": [
        "1. 检查无线开关是否开启（笔记本通常有Fn键组合）",
        "2. 重启路由器（拔电源等30秒再插上）",
        "3. 在电脑上'忘记'该WiFi后重新连接",
        "4. 更新无线网卡驱动",
        "5. 如果其他设备能连但本机不行，可能是网卡问题",
    ],
    "手机卡顿": [
        "1. 清理后台运行的应",
        "2. 清除缓存：设置 -> 存储 -> 缓存数据 -> 清除",
        "3. 检查存储空间是否充足（建议保留至少10%剩余空间）",
        "4. 重启手机",
        "5. 备份数据后恢复出厂设置（终极手段）",
    ],
    "充电缓慢": [
        "1. 确认使用的是原装充电器和数据线",
        "2. 检查充电口是否有灰尘或异物",
        "3. 充电时尽量不要使用手机，尤其是玩游戏",
        "4. 如果支持快充，确认开启了快充功能",
        "5. 电池温度过高时充电速度会降低，冷却后再充",
    ],
}


def tech_diagnosis(issue: str) -> str:
    """技术诊断，返回对应解决方案"""
    for key, steps in tech_tips.items():
        if issue.lower() in key.lower():
            return f"关于【{key}】的解决方案：\n" + "\n".join(f"  {s}" for s in steps)
    return (
        f"关于您提到的【{issue}】问题，我没有找到精确匹配的解决方案。\n"
        f"建议您：\n"
        f"1. 尝试重启设备（解决90%的问题）\n"
        f"2. 检查是否有系统/软件更新\n"
        f"3. 如需进一步帮助，请联系人工技术支持"
    )
