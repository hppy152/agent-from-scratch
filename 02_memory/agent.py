"""
Level 2 · 我开始记住事情
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

我有三层记忆了：
  - 短期：当前对话的消息列表
  - 中期：对话太长时自动压缩为摘要
  - 长期：重要的事实保存到文件，跨对话不丢

运行: python agent.py
"""

import json
from openai import OpenAI
from tools import TOOL_SCHEMAS, execute_tool
from memory import ConversationBuffer, LongTermMemory, extract_facts_from_message

# ── 大脑 ────────────────────────────────
client = OpenAI()

SYSTEM_PROMPT = """你是一个有记忆的Agent。
你能记住对话中的重要信息（用户名字、偏好、约定等）。
当用户告诉你重要信息时，你会说"我记住了"。
当对话中涉及之前提到的信息时，你会主动回忆。
回答要简洁、准确。"""


def chat(buffer: ConversationBuffer, ltm: LongTermMemory, user_input: str) -> str:
    """
    核心循环的 v2 版本：
    1. 加载长期记忆作为上下文
    2. 加入短期记忆（对话历史）
    3. LLM 可能调用工具
    4. 自动提取值得记住的事实
    """

    # ── 构建带记忆的上下文 ────────────────

    # 把长期记忆注入 system prompt
    ltm_context = ltm.recall()
    messages = buffer.get_messages()

    # 在 system prompt 后面追加长期记忆
    if ltm_context:
        messages[0] = {
            "role": "system",
            "content": SYSTEM_PROMPT + f"\n\n你记得的长期记忆：\n{ltm_context}"
        }

    # ── 正常的 agent 循环（和 Level 1 一样）──

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOL_SCHEMAS,
        tool_choice="auto",
    )

    msg = response.choices[0].message

    # 处理工具调用
    if msg.tool_calls:
        messages.append(msg)
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = execute_tool(name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        msg = response.choices[0].message

    # ── 保存记忆 ──────────────────────────

    # 把用户消息和 Agent 回复加入短期记忆
    buffer.add({"role": "user", "content": user_input})
    buffer.add({"role": "assistant", "content": msg.content})

    # 自动提取值得长期记忆的事实
    facts = extract_facts_from_message(user_input)
    for fact in facts:
        ltm.remember(fact, category="user_info")

    return msg.content


def main():
    # 初始化记忆系统
    buffer = ConversationBuffer(max_messages=20)
    ltm = LongTermMemory("long_term_memory.json")

    # System prompt 作为对话的第一条消息
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
