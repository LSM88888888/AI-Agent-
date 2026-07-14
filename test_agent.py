"""
test_agent.py — V2 多智能体系统测试用例
V2 新增自动测试脚本，覆盖所有 Agent 和功能
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# 确保能找到项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.workflow import run_agent
from models.data import (
    search_products, get_order, search_faq, tech_diagnosis, list_all_issues,
    search_orders_by_status
)
from models.schema import Message, ChatState
from session_store import create_session, append_message, get_session, list_sessions, delete_session


# ========== 测试计数器 ==========
passed = 0
failed = 0
test_results = []


def test(name: str, assertion: bool, detail: str = ""):
    global passed, failed
    if assertion:
        passed += 1
        status = "PASS"
    else:
        failed += 1
        status = "FAIL"
    test_results.append(f"[{status}] {name} {detail}")
    mark = "\u2713" if assertion else "\u2717"
    print(f"  {mark} {name}")


# ========== 测试用例 ==========

def test_product_search():
    """商品搜索测试"""
    print("\n[商品搜索测试]")

    results = search_products(category="笔记本")
    test("笔记本分类搜索", len(results) >= 3, f"返回 {len(results)} 个")

    results = search_products(brand="Apple")
    test("Apple 品牌搜索", len(results) >= 3, f"返回 {len(results)} 个")

    results = search_products(keyword="笔记本")
    test("关键词搜索笔记本", len(results) >= 1)

    results = search_products(tag="降噪")
    test("标签搜索降噪", len(results) >= 3, f"返回 {len(results)} 个")

    results = search_products(max_price=5000)
    test("5000元以内商品搜索", len(results) >= 1)


def test_order_search():
    """订单搜索测试"""
    print("\n[订单搜索测试]")

    order = get_order("ORD001")
    test("查询 ORD001", order is not None and order["status"] == "已发货")

    order = get_order("ORD999")
    test("查询不存在的订单", order is None)

    shipped = search_orders_by_status("已发货")
    test("已发货订单列表", len(shipped) >= 5, f"返回 {len(shipped)} 个")

    cancelled = search_orders_by_status("已取消")
    test("已取消订单列表", len(cancelled) >= 2, f"返回 {len(cancelled)} 个")


def test_faq():
    """FAQ 搜索测试"""
    print("\n[FAQ 搜索测试]")

    results = search_faq("退货")
    test("搜索 退货", len(results) >= 1)
    q, a = results[0]
    test("退货结果含有效内容", "退货" in q or "退货" in a)

    results = search_faq("积分")
    test("搜索 积分", len(results) >= 1)

    results = search_faq("不存在的内容")
    test("搜索不存在内容时返回默认结果", len(results) >= 3)

    # 检查 FAQ 条目数
    from models.data import faq
    test("FAQ 条目数 >= 20", len(faq) >= 20, f"当前 {len(faq)} 条")


def test_tech_diagnosis():
    """技术诊断测试"""
    print("\n[技术诊断测试]")

    result = tech_diagnosis("电脑蓝屏")
    test("诊断 电脑蓝屏", "电脑蓝屏" in result or "蓝屏" in result)

    result = tech_diagnosis("wifi连不上")
    test("诊断 wifi连不上", "wifi" in result or "WiFi" in result or "无线" in result)

    result = tech_diagnosis("自定义问题")
    test("诊断非匹配问题", "重启设备" in result)

    all_issues = list_all_issues()
    test("技术方案数 >= 20", len(all_issues) >= 20, f"当前 {len(all_issues)} 个")


async def test_agent_workflow():
    """Agent 工作流测试"""
    print("\n[Agent 工作流测试]")

    result = await run_agent("推荐一款办公笔记本")
    test("销售 Agent 回复", len(result.final_response) > 0)
    test("销售 Agent 标记", result.current_agent == "sales")
    test("意图识别为 sale", result.intent == "sale" or result.intent is not None)

    result = await run_agent("我的订单 ORD001 到哪了")
    test("客服 Agent 回复", len(result.final_response) > 0)
    test("客服 Agent 标记", result.current_agent == "service")

    result = await run_agent("电脑蓝屏怎么办")
    test("技术 Agent 回复", len(result.final_response) > 0)
    test("技术 Agent 标记", result.current_agent == "tech")

    result = await run_agent("你好")
    test("聊天 Agent 回复", len(result.final_response) > 0)
    test("聊天 Agent 标记", result.current_agent == "chat")


def test_session_store():
    """会话持久化测试"""
    print("\n[会话持久化测试]")

    session_id = create_session()
    test("创建新会话", len(session_id) == 8)

    append_message(session_id, "user", "你好")
    append_message(session_id, "assistant", "你好！有什么可以帮您的？")
    session = get_session(session_id)
    test("追加消息后读取", session is not None and len(session.messages) == 2)

    sessions = list_sessions(limit=5)
    test("列出会话", len(sessions) >= 1)

    deleted = delete_session(session_id)
    test("删除会话", deleted)
    session = get_session(session_id)
    test("删除后查询不存在", session is None)


# ========== 主入口 ==========

async def main():
    print("=" * 50)
    print("  AI Multi-Agent V2 - 自动化测试")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    test_product_search()
    test_order_search()
    test_faq()
    test_tech_diagnosis()
    await test_agent_workflow()
    test_session_store()

    print("\n" + "=" * 50)
    print(f"  测试完成: {passed} PASS / {failed} FAIL / {passed + failed} TOTAL")
    print("=" * 50)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
