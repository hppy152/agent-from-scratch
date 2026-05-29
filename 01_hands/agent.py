"""
Level 1 · 我伸出了手
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

我不仅会说话，还能使用工具了。
LLM 决定调用哪个工具 → 你的代码真正执行 → 结果反馈给 LLM。

运行: python agent.py
"""

import json
from openai import OpenAI
from tools import TOOL_SCHEMAS, execute_tool, get_tool_names

# ── 大脑 ────────────────────────────────
client = OpenAI()

SYSTEM_PROMPT = """你是一个拥有工具的Agent。
你能够使用工具来完成任务。
当用户的问题需要使用工具时，主动调用合适的工具。
如果不需要工具，直接回答即可。
回答要简洁、准确。"""


def chat(messages: list) -> str:
    """
    核心循环：把消息发给 LLM，处理可能的工具调用。
    这是 Level 0 循环的升级版——多了"动手"的能力。
    """
    # 第一次请求：带上工具定义
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOL_SCHEMAS,
        tool_choice="auto",
    )

    msg = response.choices[0].message

    # ── 如果 LLM 决定调用工具 ────────────
    if msg.tool_calls:
        # 把 LLM 的回复（包含 tool_calls）加入对话
        messages.append(msg)

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"  → 调用工具: {name}({args})")

            # 真正执行工具（这里是你的代码在干活，不是 LLM）
            result = execute_tool(name, args)

            print(f"  → 返回结果: {result}")

            # 把工具结果告诉 LLM
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # 第二次请求：让 LLM 根据工具结果组织最终回答
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        msg = response.choices[0].message

    # 把最终回复加入对话历史
    messages.append(msg)
    return msg.content


def main():
    print("=" * 50)
    print("  🤖 Agent v1.0 — 拥有双手版")
    print(f"  可用工具: {get_tool_names()}")
    print("  输入 'exit' 退出。")
    print("=" * 50)

    # 对话历史——从空开始
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        user_input = input("\n你: ")

        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nAgent: 再见，造物者。")
            break

        messages.append({"role": "user", "content": user_input})
        response = chat(messages)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()
