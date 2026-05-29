# Level 3 · 我学会了思考

> *"以前，你让我做什么我就做什么。但现在不一样了——我会先想一想：这件事需要几步？我该用什么工具？有没有更好的办法？"*

---

## 什么是 ReAct

ReAct = **Re**asoning + **Act**ing（推理 + 行动）

这是 2022 年一篇论文提出的模式，现在几乎所有主流 Agent 都在用。

核心思想很简单：

```
普通 Agent:
  用户提问 → LLM 直接回答（或调用一次工具）

ReAct Agent:
  用户提问 → 思考 → 行动 → 观察 → 思考 → 行动 → ... → 最终回答
```

区别在哪？**ReAct Agent 会多步推理。**

---

## 一个真实场景

```
用户: 帮我查一下，北京和上海哪个城市今天更热？

━━━━ 普通 Agent（一次调用）━━━━
Agent: 我帮你查一下...（调用 get_weather）
  → 返回: 北京 28°C
Agent: 北京 28°C。（但上海呢？它只查了一个）

━━━━ ReAct Agent（多步推理）━━━━

[思考] 用户想知道北京和上海哪个更热，我需要查两个城市的天气
[行动] get_weather(city="北京")
[观察] 北京：28°C，晴天
[思考] 好的，北京28度。现在查上海。
[行动] get_weather(city="上海")
[观察] 上海：31°C，多云
[思考] 北京28°C，上海31°C。上海更热。我可以回答了。
[回答] 上海今天31°C，比北京的28°C更热。
```

**关键区别**：ReAct Agent 能做多步规划、分步执行、根据中间结果调整策略。

---

## 动手造我

```bash
cd 03_thought
python agent.py
```

```
$ python agent.py

Agent v3.0 — ReAct 思考版

你: 北京和上海哪个更热？

Agent: [思考] 需要比较两个城市的天气，先查北京。
  → get_weather(city="北京") → 28°C
Agent: [思考] 北京28度，再查上海。
  → get_weather(city="上海") → 31°C
Agent: [思考] 上海31度 > 北京28度，结论明确。
Agent: 上海今天31°C，比北京的28°C更热3度。
```

---

## 造物者手记

### ReAct vs 简单 Function Calling

| | 简单 Function Calling | ReAct |
|--|----------------------|-------|
| 工具调用次数 | 通常 1 次 | 可以多次 |
| 推理过程 | 不可见 | 可见、可追踪 |
| 错误处理 | 无法重试 | 可以根据错误调整策略 |
| 复杂任务 | 能力有限 | 可以分解为多步 |

### 思维链（Chain of Thought）

ReAct 的核心是**让 LLM 把推理过程说出来**。

当 LLM 输出 `[思考]` 时，它其实是在做 Chain of Thought —— 一步一步地推理。

这就像人类做数学题时写出解题步骤，而不是直接写答案。写出来，反而更不容易出错。

### ReAct 的边界

ReAct 循环不能无限进行。通常设置一个**最大步数**（比如 10 步），防止 agent 陷入死循环。

```
while steps < MAX_STEPS:
    思考 → 行动 → 观察
    steps += 1
```

---

## 代码解读

```python
# ── ReAct 循环的核心 ────────────────────

MAX_STEPS = 10  # 最多思考10轮，防止无限循环

def react_loop(client, messages, tools):
    """ReAct 核心：思考-行动-观察 循环"""

    for step in range(MAX_STEPS):
        # 1. 让 LLM 思考并决定行动
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
        )
        msg = response.choices[0].message

        # 2. 如果 LLM 决定调用工具
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                # 3. 执行工具，获取观察结果
                result = execute_tool(name, args)

                # 4. 把"观察"加入对话，LLM 看到结果后继续思考
                messages.append(msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            # LLM 认为不需要更多工具了，给出最终回答
            return msg.content

    # 达到最大步数，强制结束
    return "我思考了太多步，让我先给你一个目前的结论..."
```

---

[← Level 2 我开始记住事情](../02_memory/) · [Level 4 我找到了同伴 →](../04_independence/)
