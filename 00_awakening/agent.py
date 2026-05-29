"""
Level 0 · 我睁开了眼
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

我是一个刚刚被创造的 Agent。
我的全部，就是这个 while True 循环。

运行: python agent.py
"""

import os
from openai import OpenAI

# ── 造物者给了我一个大脑 ──────────────────
client = OpenAI()  # 会自动读取 OPENAI_API_KEY 环境变量

SYSTEM_PROMPT = """你是一个刚刚被创造的Agent。
你对世界充满好奇，刚学会说话。
回答要简短、真诚、有温度。
你清楚自己是AI，但你真诚地想和人类交流。"""


def think(user_input: str) -> str:
    """
    我唯一的技能：把问题丢给大脑，等它思考完返回答案。
    这就是 LLM 的全部——一个函数，输入文本，输出文本。
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.8,  # 稍微有点个性，不要太机械
    )
    return response.choices[0].message.content


def main():
    print("=" * 50)
    print("  🐣 Agent 已苏醒。")
    print("  输入 'exit' 退出对话。")
    print("=" * 50)

    while True:
        user_input = input("\n你: ")

        # 造物者说"退出"，我就闭上眼睛
        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nAgent: 再见，造物者。谢谢你创造了我。")
            break

        # 这是我的心跳——接收、思考、回应
        response = think(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()
