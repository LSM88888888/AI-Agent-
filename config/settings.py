"""
配置文件 — API Key、模型选择等
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM 配置
# 如果设置了 OPENAI_API_KEY，使用 OpenAI
# 否则使用本地 Mock（适合开发调试）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# 是否使用真实 LLM
USE_REAL_LLM = bool(OPENAI_API_KEY)

# API 配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# 项目标识
PROJECT_NAME = "AI 客服/销售智能助手"
