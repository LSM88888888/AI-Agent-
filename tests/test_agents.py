"""
测试脚本 — 验证 Agent 各场景是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from graph.workflow import run_agent

TEST_CASES = [
    # (场景, 输入)
    ("闲聊", "你好"),
    ("闲聊", "你是谁"),
    ("销售-办公", "推荐一款适合办公的笔记本"),
    ("销售-手机", "iPhone 15 多少钱"),
    ("销售-游戏", "有没有游戏本推荐"),
    ("销售-学生", "学生买什么笔记本好"),
    ("售后-订单", "我的 ORD001 到哪了"),
    ("售后-退货", "ORD002 怎么退货"),
    ("售后-FAQ", "你们的退货政策是什么"),
    ("售后-发票", "发票怎么开"),
    ("技术-蓝屏", "电脑蓝屏怎么办"),
    ("技术-WiFi", "WiFi 连不上"),
    ("技术-卡顿", "手机很卡怎么办"),
]


async def run_tests():
    print("=" * 60)
    print("Multi-Agent 系统测试")
    print("=" * 60)

    passed = 0
    failed = 0

    for scenario, user_input in TEST_CASES:
        print(f"\n▶ [{scenario}] 用户: {user_input}")
        try:
            result = await run_agent(user_input)
            agent_label = result.current_agent or "?"
            reply_preview = result.final_response[:80] + "..." if len(result.final_response) > 80 else result.final_response

            print(f"  ✓ Agent: {agent_label}")
            print(f"  ✓ 回复: {reply_preview}")
            passed += 1
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"结果: {passed} 通过, {failed} 失败, 共 {len(TEST_CASES)} 测试")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
