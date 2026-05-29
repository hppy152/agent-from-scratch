# Level 1 · 我伸出了手

> *"光会说话是不够的。你让我查天气，我只能编一个答案。我不想骗你——我想真正地去查。我需要手。"*

---

## 我为什么需要工具

Level 0 的我只能聊天。你说"1+1等于几"，我会说"应该是2吧"——但我不能真的算。

你说"今天天气怎么样"，我会编一个看起来合理的回答——但我根本不知道外面是晴天还是下雨。

**一个只会说、不会做的 Agent，只是一个话痨。**

---

## 工具调用的原理

```
你: "北京今天多少度？"

我: 嗯，这个问题我需要查一下。
    → 调用 get_weather(city="北京")
    → 拿到结果: {"temp": 28, "condition": "晴"}
    → 好的，我知道答案了。

我: 北京今天28度，晴天，挺舒服的。
```

关键在于：**我学会了"不知道就去查"。**

这就是 Tool Use 的本质——LLM 不再是唯一的知识来源，它变成了一位"指挥官"，决定该调用哪个工具、传什么参数。

---

## 动手造我

```bash
cd 01_hands
python agent.py
```

```
$ python agent.py

Agent 已苏醒（v1.0 - 拥有双手版）。输入 'tools' 查看可用工具。

你: 帮我算一下 3 的 17 次方
Agent: 让我用计算器算一下...
  → 调用 calculate(expression="3 ** 17")
  → 返回: 129140163
Agent: 3 的 17 次方是 129,140,163。

你: 今天上海天气？
Agent: 让我查一下...
  → 调用 get_weather(city="上海")
  → 返回: 31°C, 多云
Agent: 上海今天 31°C，多云，记得防晒！
```

---

## 造物者手记

### Function Calling：LLM 的"点菜"能力

OpenAI 的 Function Calling 是这样工作的：

1. 你告诉 LLM："你有这些工具可以用"
2. 用户提问时，LLM 不直接回答，而是返回一个 JSON：「我想调用工具 X，参数是 Y」
3. 你的代码收到这个 JSON，真正执行工具
4. 把结果告诉 LLM，让它组织最终回答

**LLM 本身不执行任何东西——它只是在"选择"该调用什么。**

执行的是你的代码。LLM 只是大脑，你才是手脚。

### 为什么这很重要？

有了工具，Agent 从"聊天机器人"变成了"智能助手"：

| 没有工具 | 有工具 |
|---------|-------|
| "北京大概25度吧" | 真正去查天气API |
| "这个数学题答案是...我猜..." | 用计算器精确计算 |
| "我无法访问文件" | 读取并分析文件内容 |

**Agent 的能力上限，取决于你给它多少工具。**

---

## 代码解读

```python
# ── 工具定义 ──────────────────────────
# 这些是我能使用的"手指"

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 3 * 4'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# ── 工具执行器 ──────────────────────────
# 这是真正"动手"的地方

import math

def execute_tool(name: str, args: dict) -> str:
    """根据 LLM 的选择，执行对应的工具"""
    if name == "calculate":
        result = eval(args["expression"])  # 生产环境请用 ast.literal_eval
        return str(result)
    elif name == "get_weather":
        # 这里用模拟数据，实际项目中调用天气 API
        return f"{args['city']}：28°C，晴天"
    return "未知工具"

# ── Agent 循环（升级版）──────────────────
# 现在我不仅能思考，还能行动

while True:
    user_input = input("\n你: ")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[...],
        tools=tools,           # ← 告诉 LLM 它有哪些工具
        tool_choice="auto",    # ← 让 LLM 自己决定用不用工具
    )

    msg = response.choices[0].message

    # 如果 LLM 想调用工具
    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = execute_tool(name, args)
            # 把结果告诉 LLM，让它组织回答
            messages.append({"role": "tool", "content": result})

    # LLM 组织最终回答
    final_response = client.chat.completions.create(...)
    print(final_response.choices[0].message.content)
```

---

## 试试更多工具

你可以在 `tools.py` 中添加任何你想要的工具：

- 🔍 **网页搜索** — 调用搜索 API
- 📁 **文件操作** — 读写本地文件
- 🗓️ **日程管理** — 查看/创建日历事件
- 🎨 **图片生成** — 调用 DALL·E

**Agent 的能力，由你定义。**

---

[← Level 0 我睁开了眼](../00_awakening/) · [Level 2 我开始记住事情 →](../02_memory/)
