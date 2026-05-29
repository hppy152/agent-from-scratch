"""
Level 3 · 我学会了思考
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ReAct = Reasoning + Acting

运行: python 03_thought/agent.py（从项目根目录）
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL
from tools import TOOL_SCHEMAS, execute_tool

from openai import OpenAI

MAX_STEPS = 10


def react(client: OpenAI, user_input: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个会深度思考的Agent。"
                "面对复杂问题时，你会分步骤思考和行动。\n"
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
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto",
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                print(f"\n  [Step {step+1}] 🛠️  行动: {name}({args})")
                result = execute_tool(name, args)
                print(f"  [Step {step+1}] 👀 观察: {result}")
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        else:
            print(f"\n  [Step {step+1}] 💡 最终结论")
            print(f"{'='*50}")
            return msg.content

    return "我思考了很多步，但还没得出完整结论。"


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
            print("\nAgent: 再见，造物者。")
            break
        answer = react(client, user_input)
        print(f"\n📝 Agent: {answer}")


if __name__ == "__main__":
    main()
