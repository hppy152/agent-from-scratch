"""
Level 2 · 我开始记住事情
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

运行: python 02_memory/agent.py（从项目根目录）
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MODEL
from tools import TOOL_SCHEMAS, execute_tool
from memory import ConversationBuffer, LongTermMemory, extract_facts_from_message

from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """你是一个有记忆的Agent。
你能记住对话中的重要信息（用户名字、偏好、约定等）。
当用户告诉你重要信息时，你会说"我记住了"。
回答要简洁、准确。"""


def chat(buffer: ConversationBuffer, ltm: LongTermMemory, user_input: str) -> str:
    ltm_context = ltm.recall()
    messages = buffer.get_messages()

    if ltm_context:
        messages[0] = {
            "role": "system",
            "content": SYSTEM_PROMPT + f"\n\n你记得的长期记忆：\n{ltm_context}"
        }

    response = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto",
    )
    msg = response.choices[0].message

    if msg.tool_calls:
        messages.append(msg)
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            result = execute_tool(name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        response = client.chat.completions.create(model=MODEL, messages=messages)
        msg = response.choices[0].message

    buffer.add({"role": "user", "content": user_input})
    buffer.add({"role": "assistant", "content": msg.content})

    for fact in extract_facts_from_message(user_input):
        ltm.remember(fact, category="user_info")

    return msg.content


def main():
    buffer = ConversationBuffer(max_messages=20)
    ltm = LongTermMemory("long_term_memory.json")
    buffer.add({"role": "system", "content": SYSTEM_PROMPT})

    print("=" * 50)
    print("  🧠 Agent v2.0 — 有记忆版")
    print(f"  已加载 {ltm.count()} 条长期记忆")
    print("  输入 'memory' 查看记忆，'exit' 退出。")
    print("=" * 50)

    while True:
        user_input = input("\n你: ")
        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nAgent: 再见，造物者。我会记住我们的对话。")
            break
        if user_input.strip().lower() == "memory":
            print(f"\n长期记忆 ({ltm.count()}条):\n{ltm.recall()}")
            continue
        response = chat(buffer, ltm, user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()
