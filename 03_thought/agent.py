"""
Level 3 · 我学会了思考
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ReAct = Reasoning + Acting
  思考 → 行动 → 观察 → 思考 → 行动 → ... → 最终回答

运行: python 03_thought/agent.py（从项目根目录）
"""

import json
import sys
import os

# 从项目根目录导入共享工具模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import TOOL_SCHEMAS, execute_tool

from openai import OpenAI

# ═══════════════════════════════════════════
# ReAct 引擎
# ═══════════════════════════════════════════

MAX_STEPS = 10  # 最多思考10轮，防止 agent 陷入死循环


def react(client: OpenAI, user_input: str) -> str:
    """
    ReAct 核心循环：思考 → 行动 → 观察 → 再思考 ...

    和 Level 0-1 的区别：
    - Level 0: LLM 直接回答
    - Level 1: LLM 调用一次工具，根据结果回答
    - Level 3: LLM 可以多次调用工具，根据中间结果调整策略
    """

    messages = [
        {
            "role": "system",
            "content": (
                "你是一个会深度思考的Agent。"
                "面对复杂问题时，你会分步骤思考和行动。\n"
                "每次行动前，先在心里想清楚：\n"
                "1. 我现在知道什么？\n"
                "2. 我还需要什么信息？\n"
                "3. 我该用什么工具？\n"
                "只有当所有信息都齐了，才给出最终回答。"
            )
        },
        {"role": "user", "content": user_input}
    ]

    print(f"\n{'='*50}")
    print(f"🤔 开始思考: {user_input}")
    print(f"{'='*50}")

    for step in range(MAX_STEPS):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"\n  [Step {step + 1}] 🛠️  行动: {name}({args})")

                result = execute_tool(name, args)

                print(f"  [Step {step + 1}] 👀 观察: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            print(f"\n  [Step {step + 1}] 💡 最终结论")
            print(f"{'='*50}")
            return msg.content

    return "我思考了很多步，但还没得出完整结论。让我先告诉你目前的发现。"


def main():
    client = OpenAI()

    print("=" * 50)
    print("  🧠 Agent v3.0 — ReAct 思考版")
    print("  我会把思考过程展示给你看。")
    print("  输入 'exit' 退出。")
    print("=" * 50)

    while True:
        user_input = input("\n你: ")

        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nAgent: 再见，造物者。思考是美丽的。")
            break

        answer = react(client, user_input)
        print(f"\n📝 Agent: {answer}")


if __name__ == "__main__":
    main()
