#!/usr/bin/env python3
"""
🐣 Agent From Scratch — 一键启动器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

用法:
    python run.py          # 交互式选择 Level
    python run.py 0        # 直接启动 Level 0
    python run.py 3        # 直接启动 Level 3
"""

import sys
import os

# 确保从项目根目录运行
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

LEVELS = {
    "0": {
        "name": "Level 0 · 我睁开了眼",
        "desc": "最简对话循环 — Agent 的心跳",
        "path": "00_awakening/agent.py",
    },
    "1": {
        "name": "Level 1 · 我伸出了手",
        "desc": "工具调用 — Agent 开始触碰世界",
        "path": "01_hands/agent.py",
    },
    "2": {
        "name": "Level 2 · 我开始记住事情",
        "desc": "记忆系统 — Agent 不再遗忘",
        "path": "02_memory/agent.py",
    },
    "3": {
        "name": "Level 3 · 我学会了思考",
        "desc": "ReAct 循环 — Agent 学会推理",
        "path": "03_thought/agent.py",
    },
    "4": {
        "name": "Level 4 · 我找到了同伴",
        "desc": "多 Agent 协作 — Agent 找到同伴",
        "path": "04_independence/orchestrator.py",
    },
    "5": {
        "name": "Level 5 · 我学会了连接世界",
        "desc": "MCP + Skills — Agent 连接更大的世界",
        "path": "05_connection/agent.py",
    },
    "6": {
        "name": "Level 6 · 我有了分身",
        "desc": "SubAgent — 动态分发任务给子 Agent",
        "path": "06_subagent/agent.py",
    },
    "7": {
        "name": "Level 7 · 我会反思了",
        "desc": "自我进化 — 反思循环 + 技能库",
        "path": "07_evolution/agent.py",
    },
    "8": {
        "name": "Level 8 · 我会研究了",
        "desc": "深度研究 — 分解 → 调研 → 综合",
        "path": "08_research/agent.py",
    },
}


def print_banner():
    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║   🐣 Agent From Scratch — 女娲造人           ║")
    print("  ║   从零开始，亲手造一个 Agent                  ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()


def select_level():
    print("  选择你要造的 Agent 层级：\n")
    for key, level in LEVELS.items():
        print(f"    [{key}] {level['name']}")
        print(f"        {level['desc']}")
        print()

    while True:
        choice = input("  👉 选择 (0-4): ").strip()
        if choice in LEVELS:
            return choice
        print("  ❌ 请输入 0-4")


def main():
    # 检查 API Key
    if not os.environ.get("OPENAI_API_KEY"):
        print("  ❌ 未设置 OPENAI_API_KEY")
        print()
        print("  请先设置你的 API Key：")
        print()
        print("  OpenAI:")
        print("    export OPENAI_API_KEY='sk-xxx'")
        print()
        print("  小米 MiMo:")
        print("    export OPENAI_API_KEY='你的小米Key'")
        print("    export OPENAI_BASE_URL='https://token-plan-cn.xiaomimimo.com/v1'")
        print("    export AGENT_MODEL='mimo-v2-pro'")
        print()
        print("  获取地址: https://platform.openai.com/api-keys")
        sys.exit(1)

    # 检查 openai 包
    try:
        import openai
    except ImportError:
        print("  ❌ 未安装 openai 包")
        print()
        print("  请先安装：")
        print("    pip install openai")
        sys.exit(1)

    print_banner()

    # 如果命令行指定了 level，直接启动
    if len(sys.argv) > 1 and sys.argv[1] in LEVELS:
        level_key = sys.argv[1]
    else:
        level_key = select_level()

    level = LEVELS[level_key]
    script_path = os.path.join(ROOT, level["path"])

    print(f"\n  🚀 启动: {level['name']}")
    print(f"  📂 脚本: {level['path']}")
    print()

    # 动态导入并运行
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


if __name__ == "__main__":
    main()
