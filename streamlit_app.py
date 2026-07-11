"""
Streamlit 前端 — AI 客服/销售智能助手聊天界面
"""

import streamlit as st
import httpx
import json

# ========== 页面配置 ==========
st.set_page_config(
    page_title="AI 智能助手",
    page_icon="🖋",
    layout="centered",
)

# ========== CSS 自定义样式 ==========
st.markdown("""
<style>
    /* Agent 标签 */
    .agent-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .agent-sale { background-color: #e3f2fd; color: #1565c0; }
    .agent-service { background-color: #fce4ec; color: #c62828; }
    .agent-tech { background-color: #e8f5e9; color: #2e7d32; }
    .agent-chat { background-color: #f3e5f5; color: #7b1fa2; }

    /* 对话气泡 */
    .chat-message {
        padding: 12px 16px;
        border-radius: 18px;
        margin-bottom: 10px;
        max-width: 80%;
        word-wrap: break-word;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    /* 侧边栏提示 */
    .sidebar-hint {
        font-size: 13px;
        padding: 8px;
        margin-bottom: 8px;
        border-left: 3px solid #1976d2;
        background-color: #f5f9ff;
    }
</style>
""", unsafe_allow_html=True)

# ========== 初始化会话状态 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

API_URL = "http://localhost:8000"

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("## 🖋 AI 智能助手")
    st.markdown("---")

    st.markdown("### 试试这样问：")
    st.markdown(
        '<div class="sidebar-hint">'
        '💼 **售前咨询**<br>'
        '"推荐一款办公笔记本"<br>'
        '"iPhone 15 多少钱"'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-hint">'
        '📦 **订单服务**<br>'
        '"我的 ORD001 到哪了"<br>'
        '"怎么退货"'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-hint">'
        '🔧 **技术支持**<br>'
        '"电脑蓝屏怎么办"<br>'
        '"WiFi 连不上"'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption(f"后端地址: {API_URL}")

    if st.button("🗑 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ========== 标题 ==========
st.markdown("## 🖋 AI 客服 / 销售智能助手")
st.markdown("---")

# ========== 显示聊天历史 ==========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            agent = msg.get("agent", "")
            intent = msg.get("intent", "")
            if agent:
                badge_class = {
                    "sales": "agent-sale",
                    "service": "agent-service",
                    "tech": "agent-tech",
                    "chat": "agent-chat",
                }.get(agent, "agent-chat")
                agent_label = {
                    "sales": "💼 销售顾问",
                    "service": "📦 售后客服",
                    "tech": "🔧 技术支持",
                    "chat": "🖋 小墨",
                }.get(agent, "🖋 小墨")
                st.markdown(
                    f'<span class="agent-badge {badge_class}">{agent_label}</span>',
                    unsafe_allow_html=True,
                )
        st.markdown(msg["content"])

# ========== 输入框 ==========
if prompt := st.chat_input("请输入您的问题…"):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用后端 API
    with st.chat_message("assistant"):
        with st.spinner("思考中…"):
            try:
                resp = httpx.post(
                    f"{API_URL}/chat",
                    json={"message": prompt},
                    timeout=30,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    reply = data.get("reply", "")
                    agent = data.get("agent", "")
                    intent = data.get("intent", "")

                    # 显示 Agent 标签
                    if agent:
                        badge_class = {
                            "sales": "agent-sale",
                            "service": "agent-service",
                            "tech": "agent-tech",
                            "chat": "agent-chat",
                        }.get(agent, "agent-chat")
                        agent_label = {
                            "sales": "💼 销售顾问",
                            "service": "📦 售后客服",
                            "tech": "🔧 技术支持",
                            "chat": "🖋 小墨",
                        }.get(agent, "🖋 小墨")
                        st.markdown(
                            f'<span class="agent-badge {badge_class}">{agent_label}</span>',
                            unsafe_allow_html=True,
                        )
                    st.markdown(reply)

                    # 保存到历史
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply,
                        "agent": agent,
                        "intent": intent,
                    })
                else:
                    err_msg = f"请求失败 (HTTP {resp.status_code})"
                    st.error(err_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": err_msg,
                    })
            except Exception as e:
                err_msg = f"⚠️ 连接后端失败：{e}\n\n请确保后端服务已启动（`python main.py`）"
                st.error(err_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err_msg,
                })
