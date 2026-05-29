"""
全局配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

通过环境变量配置，兼容任何 OpenAI 兼容 API。

环境变量:
    OPENAI_API_KEY    - API Key（必需）
    OPENAI_BASE_URL   - API 地址（可选，默认 OpenAI）
    AGENT_MODEL       - 模型名称（可选，默认 gpt-4o-mini）
"""

import os

# ── 模型配置 ──────────────────────────────
# 可通过环境变量 AGENT_MODEL 覆盖
# 小米 MiMo: mimo-v2-pro
# OpenAI:    gpt-4o-mini, gpt-4o
# 其他:      根据你的 API 提供商设置
MODEL = os.environ.get("AGENT_MODEL", "gpt-4o-mini")

# ── API 配置 ──────────────────────────────
API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = os.environ.get("OPENAI_BASE_URL", None)  # None = 用 OpenAI 默认
