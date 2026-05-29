"""
Level 3 · 我学会了思考
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ReAct = Reasoning + Acting
  思考 → 行动 → 观察 → 思考 → 行动 → ... → 最终回答

运行: python agent.py
"""

import json
from openai import OpenAI

# ── 工具定义（和 Level 1 一样，但这里精简了）──

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "搜索信息（模拟搜索引擎）",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名"}
                },
                "required": ["city"]
            }
        }
    },
]


def execute_tool(name: str, args: dict) -> str:
    """执行工具"""
    import random
    from datetime import datetime

    if name == "calculate":
        try:
            result = eval(args["expression"], {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"计算错误: {e}"

    elif name == "search":
        query = args["query"]
        # 模拟搜索结果
        return (
            f"搜索 '{query}' 的结果：\n"
            f"1. 关于{query}的最新资讯\n"
            f"2. {query}的详细分析\n"
            f"3. {query}相关讨论"
        )

    elif name == "get_weather":
        city = args["city"]
        random.seed(hash(city) + datetime.now().day)
        temp = random.randint(15, 35)
        condition = random.choice(["晴天", "多云", "小雨", "阴天"])
        return f"{city}：{temp}°C，{condition}"

    return "未知工具"


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

    # 初始消息
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
        # ── Step 1: 让 LLM 思考 ──────────
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        # ── Step 2: 如果 LLM 决定行动 ────
        if msg.tool_calls:
            messages.append(msg)

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"\n  [Step {step + 1}] 🛠️  行动: {name}({args})")

                # 执行工具，获取"观察"结果
                result = execute_tool(name, args)

                print(f"  [Step {step + 1}] 👀 观察: {result}")

                # 把观察结果告诉 LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            # ── Step 3: LLM 认为可以回答了 ──
            print(f"\n  [Step {step + 1}] 💡 最终结论")
            print(f"{'='*50}")
            return msg.content

    # 达到最大步数
    return "我思考了很多步，但还没得出完整结论。让我先告诉你目前的发现。"


# ═══════════════════════════════════════════
# 主循环
# ═══════════════════════════════════════════

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
