"""
模拟数据 — 商品、订单、FAQ、技术知识库 (V2)
V2 更新：
- 商品数据复用项目一的 products.json（31+ 款）
- 订单数据扩充到 30+
- FAQ 扩充到 20+
- 技术方案扩充到 20+
"""

import json
import os
from typing import Optional, List

# ========== 商品（复用项目一的 products.json）==========
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# data.py at .../projects/ai-multi-agent/models/data.py
# Project1 root = above 3 levels: ai-multi-agent -> projects -> ai-knowledge-assistant
_Products_PATH = os.path.join(os.path.dirname(_PROJECT_ROOT), "products.json")

def _load_products():
    """加载项目一的商品数据"""
    try:
        with open(_Products_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback: 如果找不到项目一的数据，使用内置数据
        return []

_products_list = _load_products()

# 转换为字典格式，方便按名称查找
products = {}
for p in _products_list:
    key = f"{p['category']}-{p.get('subcategory', '通用')}"
    products[p['id']] = {
        "name": p['name'],
        "brand": p.get('brand', ''),
        "category": p['category'],
        "subcategory": p.get('subcategory', ''),
        "price": p['price'],
        "original_price": p.get('original_price', p['price']),
        "stock": p.get('stock', 0),
        "rating": p.get('rating', 4.5),
        "sales_count": p.get('sales_count', 0),
        "tags": p.get('tags', []),
        "desc": p.get('desc', ''),
        "specs": p.get('specs', {}),
    }


def search_products(**kwargs) -> List[dict]:
    """按条件搜索商品（V2 增强版）"""
    result = list(products.values())
    for key, val in kwargs.items():
        if key == "category":
            result = [p for p in result if p["category"] == val]
        elif key == "subcategory":
            result = [p for p in result if p.get("subcategory") == val]
        elif key == "brand":
            result = [p for p in result if p.get("brand") == val]
        elif key == "max_price":
            result = [p for p in result if p["price"] <= val]
        elif key == "min_price":
            result = [p for p in result if p["price"] >= val]
        elif key == "keyword":
            val_lower = val.lower()
            result = [
                p for p in result
                if val_lower in p["name"].lower()
                or val_lower in p.get("desc", "").lower()
                or val_lower in p.get("brand", "").lower()
                or any(val_lower in tag.lower() for tag in p.get("tags", []))
            ]
        elif key == "tag":
            result = [p for p in result if val in p.get("tags", [])]
    return result


def get_product_by_name(name: str) -> Optional[dict]:
    """根据商品名称查找"""
    for p in products.values():
        if name.lower() in p["name"].lower():
            return p
    return None


# ========== 订单（扩充到 30+）==========
orders = {
    # 已发货
    "ORD001": {"status": "已发货", "item": "ThinkPad X1 Carbon Gen 12", "price": 10999, "date": "2026-07-08", "logistics": "顺丰 SF1234567890", "expected_arrival": "2026-07-12"},
    "ORD002": {"status": "待发货", "item": "iPhone 16 Pro Max", "price": 9999, "date": "2026-07-10", "logistics": None, "expected_arrival": "预计2026-07-14前送达"},
    "ORD003": {"status": "已完成", "item": "AirPods Pro 2 (USB-C)", "price": 1899, "date": "2026-07-01", "logistics": "顺丰 SF9876543210", "expected_arrival": "2026-07-04"},
    "ORD004": {"status": "已取消", "item": "小米14", "price": 3999, "date": "2026-07-05", "logistics": None, "expected_arrival": "已取消"},
    "ORD005": {"status": "已发货", "item": "MacBook Air M3", "price": 8999, "date": "2026-07-09", "logistics": "京东物流 JD4567890123", "expected_arrival": "2026-07-13"},
    "ORD006": {"status": "已完成", "item": "ROG 枪神7 Plus", "price": 14999, "date": "2026-06-28", "logistics": "顺丰 SF1112223334", "expected_arrival": "2026-07-01"},
    "ORD007": {"status": "待发货", "item": "华为 MateBook X Pro 2024", "price": 11999, "date": "2026-07-11", "logistics": None, "expected_arrival": "预计2026-07-15前送达"},
    "ORD008": {"status": "已发货", "item": "iPad Pro M4 (13寸)", "price": 8499, "date": "2026-07-07", "logistics": "中通 ZTO5556667778", "expected_arrival": "2026-07-11"},
    "ORD009": {"status": "已完成", "item": "Sony WH-1000XM6", "price": 2499, "date": "2026-06-25", "logistics": "顺丰 SF9998887776", "expected_arrival": "2026-06-28"},
    "ORD010": {"status": "已取消", "item": "Anker 67W GaN充电器", "price": 259, "date": "2026-07-06", "logistics": None, "expected_arrival": "已取消"},
    "ORD011": {"status": "已发货", "item": "小米15 Pro", "price": 4999, "date": "2026-07-10", "logistics": "京东物流 JD7778889990", "expected_arrival": "2026-07-14"},
    "ORD012": {"status": "待发货", "item": "华为 Pura 70 Ultra", "price": 7999, "date": "2026-07-12", "logistics": None, "expected_arrival": "预计2026-07-16前送达"},
    "ORD013": {"status": "已完成", "item": "Apple Watch Ultra 2", "price": 5999, "date": "2026-06-20", "logistics": "顺丰 SF4445556667", "expected_arrival": "2026-06-23"},
    "ORD014": {"status": "已发货", "item": "联想小新Pro 16", "price": 5999, "date": "2026-07-09", "logistics": "圆通 YTO3334445556", "expected_arrival": "2026-07-13"},
    "ORD015": {"status": "已完成", "item": "Redmi Note 14 Pro+", "price": 1899, "date": "2026-06-15", "logistics": "中通 ZTO2223334445", "expected_arrival": "2026-06-18"},
    "ORD016": {"status": "待发货", "item": "Dell XPS 14", "price": 12999, "date": "2026-07-13", "logistics": None, "expected_arrival": "预计2026-07-17前送达"},
    "ORD017": {"status": "已发货", "item": "华为 MatePad Pro 13.2", "price": 4199, "date": "2026-07-08", "logistics": "顺丰 SF6667778889", "expected_arrival": "2026-07-12"},
    "ORD018": {"status": "已完成", "item": "Bose QC Ultra 头戴", "price": 2999, "date": "2026-06-22", "logistics": "京东物流 JD2223334445", "expected_arrival": "2026-06-25"},
    "ORD019": {"status": "已取消", "item": "iPhone 16 Pro", "price": 8999, "date": "2026-07-04", "logistics": None, "expected_arrival": "已取消"},
    "ORD020": {"status": "已发货", "item": "小米平板 7 Pro", "price": 2999, "date": "2026-07-09", "logistics": "韵达 YD1112223334", "expected_arrival": "2026-07-13"},
    "ORD021": {"status": "待发货", "item": "荣耀 Magic V3", "price": 8999, "date": "2026-07-11", "logistics": None, "expected_arrival": "预计2026-07-15前送达"},
    "ORD022": {"status": "已完成", "item": "Apple Watch Series 10", "price": 2999, "date": "2026-06-18", "logistics": "顺丰 SF8889990001", "expected_arrival": "2026-06-21"},
    "ORD023": {"status": "已发货", "item": "小米手环 9 Pro", "price": 349, "date": "2026-07-10", "logistics": "中通 ZTO4445556667", "expected_arrival": "2026-07-14"},
    "ORD024": {"status": "已取消", "item": "华为 WATCH GT 4", "price": 1588, "date": "2026-07-03", "logistics": None, "expected_arrival": "已取消"},
    "ORD025": {"status": "已完成", "item": "Samsung Galaxy Buds3 Pro", "price": 1599, "date": "2026-06-30", "logistics": "顺丰 SF3334445556", "expected_arrival": "2026-07-03"},
    "ORD026": {"status": "已发货", "item": "小米 Buds 5", "price": 699, "date": "2026-07-09", "logistics": "圆通 YTO6667778889", "expected_arrival": "2026-07-13"},
    "ORD027": {"status": "待发货", "item": "倍思 20000mAh移动电源", "price": 159, "date": "2026-07-12", "logistics": None, "expected_arrival": "预计2026-07-16前送达"},
    "ORD028": {"status": "已完成", "item": "iPad Air M2", "price": 4799, "date": "2026-06-20", "logistics": "京东物流 JD5556667778", "expected_arrival": "2026-06-23"},
    "ORD029": {"status": "已发货", "item": "Anker 100W USB-C数据线", "price": 89, "date": "2026-07-08", "logistics": "中通 ZTO7778889990", "expected_arrival": "2026-07-12"},
    "ORD030": {"status": "已取消", "item": "iPhone 16 Pro 保护壳", "price": 299, "date": "2026-07-02", "logistics": None, "expected_arrival": "已取消"},
    "ORD031": {"status": "已完成", "item": "倍思 iPhone 16 Pro 钢化膜", "price": 45, "date": "2026-06-25", "logistics": "韵达 YD2223334445", "expected_arrival": "2026-06-28"},
}


def get_order(order_id: str) -> Optional[dict]:
    """根据订单号查询订单"""
    return orders.get(order_id.upper())


def search_orders_by_status(status: str) -> List[dict]:
    """按状态搜索订单"""
    results = []
    for oid, order in orders.items():
        if order["status"] == status:
            results.append({"order_id": oid, **order})
    return results


# ========== 售后/FAQ（扩充到 20+）==========
faq = {
    "退货政策": "签收后7天内可无理由退货，需保持商品完好、配件齐全、包装完整。退回运费由买家承担（商品质量问题除外）。",
    "换货政策": "签收后15天内，如出现非人为质量问题，可免费换货。",
    "保修期限": "所有电子产品享有一年官方保修。保修期内非人为损坏免费维修。",
    "发货时间": "工作日6:00前下单，当天发货；6:00后下单，次日发货。节假日顺延。",
    "退款时间": "退货审核通过后，退款将在3-5个工作日内原路返回。",
    "配送范围": "全国范围（港澳台地区除外）均可配送，部分偏远地区时效可能延长。",
    "支付方式": "支持支付宝、微信支付、银行卡、花呗分期（3/6/12期）。",
    "发票说明": "支持电子发票和纸质发票，下单时选择即可。电子发票将在发货后发送到邮箱。",
    "价格保护": "下单后7天内，如商品降价可申请价保退差价。限时秒杀、优惠券活动不参与价保。",
    "积分规则": "每消费1元积1分，积分可用于抵扣订单金额（100积分=1元）或兑换礼品。",
    "会员权益": "注册会员享专属折扣、生日礼券、优先发货、专属客服等权益。",
    "商品验货": "签收前请当面验货，如有破损或短缺请拒收并联系客服。签收后发现问题需在24小时内反馈。",
    "物流查询": "订单发货后，可在订单详情页查看物流信息。也可通过快递公司官网或客服电话查询。",
    "修改地址": "订单未发货前可修改收货地址，已发货后无法修改。请联系客服协助处理。",
    "取消订单": "订单未发货前可在订单页面自助取消。已发货订单需签收后申请退货。",
    "商品缺货": "如商品暂时缺货，可选择到货通知或退款。预售商品按页面标注时间发货。",
    "以旧换新": "支持手机、平板、笔记本以旧换新，在线估价后寄送旧机，验收通过后发放抵扣券。",
    "企业采购": "企业用户可申请专属折扣和账期服务，联系企业客服获取方案。",
    "延保服务": "可在下单时购买延保服务，延长保修期至2-3年，含意外损坏保障。",
    "安装服务": "大家电和办公设备提供免费上门安装服务，下单时预约即可。",
    "数据迁移": "购买新手机/电脑可享受免费数据迁移服务，需预约到店或上门服务。",
    "隐私保护": "我们严格遵守隐私政策，不会泄露您的个人信息。维修时会清除设备数据。",
}


def search_faq(keyword: str) -> List[tuple]:
    """搜索FAQ，返回匹配的 (问题, 答案) 列表"""
    results = []
    keyword_lower = keyword.lower()
    for question, answer in faq.items():
        if keyword_lower in question.lower() or keyword_lower in answer.lower():
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


# ========== 技术支持（扩充到 20+）==========
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
        "1. 清理后台运行的应用",
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
    "屏幕闪烁": [
        "1. 检查屏幕连接线是否松动",
        "2. 更新显卡驱动到最新版本",
        "3. 调整屏幕刷新率设置",
        "4. 检查周围是否有强电磁干扰源",
        "5. 如问题持续，可能是屏幕硬件故障",
    ],
    "耳机没声音": [
        "1. 检查耳机是否正确插入或蓝牙是否连接",
        "2. 确认音量不是静音状态",
        "3. 在设置中检查音频输出设备选择",
        "4. 尝试在其他设备上测试耳机",
        "5. 清洁耳机接口或重置蓝牙连接",
    ],
    "电池耗电快": [
        "1. 检查是否有应用在后台大量耗电",
        "2. 降低屏幕亮度",
        "3. 关闭不必要的定位、蓝牙、WiFi",
        "4. 开启省电模式",
        "5. 检查电池健康度，老化严重的电池建议更换",
    ],
    "摄像头模糊": [
        "1. 清洁摄像头镜头表面",
        "2. 检查是否有保护膜或手机壳遮挡",
        "3. 在设置中重置相机应用",
        "4. 检查对焦模式设置",
        "5. 如硬件损坏，建议送修更换摄像头模组",
    ],
    "无法开机": [
        "1. 确认设备有电，充电15分钟后再尝试",
        "2. 强制重启（长按电源键10秒以上）",
        "3. 检查充电器和数据线是否正常工作",
        "4. 尝试进入恢复模式",
        "5. 如以上方法无效，可能是主板故障，建议送修",
    ],
    "触摸屏失灵": [
        "1. 清洁屏幕表面，去除水渍和油污",
        "2. 重启设备",
        "3. 移除屏幕保护膜测试",
        "4. 检查是否有系统更新",
        "5. 如部分区域失灵，可能是屏幕硬件问题",
    ],
    "声音杂音": [
        "1. 检查扬声器孔是否被灰尘堵塞",
        "2. 尝试使用耳机测试是否为扬声器问题",
        "3. 关闭音频增强功能",
        "4. 更新声卡驱动",
        "5. 如硬件损坏，建议更换扬声器",
    ],
    "发热严重": [
        "1. 关闭后台不必要的应用",
        "2. 避免边充电边使用",
        "3. 取下手机壳帮助散热",
        "4. 避免在高温环境下使用",
        "5. 如异常发热，可能是电池或主板问题，建议检测",
    ],
    "系统更新失败": [
        "1. 确保设备电量充足（至少50%）",
        "2. 连接稳定的WiFi网络",
        "3. 清理存储空间，确保有足够空间下载更新",
        "4. 重启后再次尝试更新",
        "5. 如多次失败，可尝试通过电脑刷机",
    ],
    "应用闪退": [
        "1. 清除应用缓存和数据",
        "2. 卸载后重新安装应用",
        "3. 检查应用是否有更新版本",
        "4. 重启设备",
        "5. 如多个应用闪退，可能是系统问题，建议恢复出厂设置",
    ],
    "蓝牙连接不上": [
        "1. 确认蓝牙设备处于配对模式",
        "2. 关闭再重新开启蓝牙",
        "3. 删除已配对记录后重新配对",
        "4. 检查设备是否在有效范围内（10米内）",
        "5. 重启两台设备后再次尝试",
    ],
    "存储空间不足": [
        "1. 删除不常用的应用",
        "2. 清理应用缓存和临时文件",
        "3. 将照片、视频备份到云端后删除本地文件",
        "4. 使用清理工具扫描大文件",
        "5. 考虑扩展存储（如支持SD卡）或升级设备",
    ],
    "指纹识别失灵": [
        "1. 清洁指纹识别区域",
        "2. 删除旧指纹重新录入",
        "3. 确保手指干燥无污渍",
        "4. 检查是否有系统更新",
        "5. 如硬件损坏，建议送修更换指纹模块",
    ],
    "网络信号差": [
        "1. 检查SIM卡是否插好",
        "2. 尝试切换飞行模式再关闭",
        "3. 更换位置测试是否为区域信号问题",
        "4. 重置网络设置",
        "5. 如持续信号差，可能是天线问题，建议检测",
    ],
    "相机黑屏": [
        "1. 重启相机应用",
        "2. 重启设备",
        "3. 检查是否有其他应用占用摄像头",
        "4. 在设置中重置相机应用",
        "5. 如硬件故障，建议更换摄像头模组",
    ],
    "键盘失灵": [
        "1. 检查键盘连接线或蓝牙连接",
        "2. 重启设备",
        "3. 尝试外接USB键盘测试",
        "4. 更新键盘驱动",
        "5. 如个别按键失灵，可能是键盘硬件问题，建议更换",
    ],
}


def tech_diagnosis(issue: str) -> str:
    """技术诊断，返回对应解决方案"""
    issue_lower = issue.lower()
    for key, steps in tech_tips.items():
        if issue_lower in key.lower() or key.lower() in issue_lower:
            return f"关于【{key}】的解决方案：\n" + "\n".join(f"  {s}" for s in steps)
    return (
        f"关于您提到的【{issue}】问题，我没有找到精确匹配的解决方案。\n"
        f"建议您：\n"
        f"1. 尝试重启设备（解决90%的问题）\n"
        f"2. 检查是否有系统/软件更新\n"
        f"3. 如需进一步帮助，请联系人工技术支持"
    )


def list_all_issues() -> List[str]:
    """列出所有支持的技术问题"""
    return list(tech_tips.keys())
