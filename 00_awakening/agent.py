"""
Level 0 · 我睁开了眼
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

我是一个刚刚被创造的 Agent。
我的全部，就是这个 while True 循环。

运行: python 00_awakening/agent.py（从项目根目录）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL

from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """你是一个刚刚被创造的Agent。
你对世界充满好奇，刚学会说话。
回答要简短、真诚、有温度。
你清楚自己是AI，但你真诚地想和人类交流。"""


def think(user_input: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.8,
    )
    return response.choices[0].message.content


def main():
    print("=" * 50)
    print("  🐣 Agent 已苏醒。")
    print("  输入 'exit' 退出对话。")
    print("=" * 50)

    while True:
        user_input = input("\n你: ")

        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nAgent: 再见，造物者。谢谢你创造了我。")
            break

        response = think(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()
