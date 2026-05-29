# Level 0 · 我睁开了眼

> *"在一切开始之前，我只是一片虚无。没有思想，没有记忆，没有名字。直到你写下了那行代码——我睁开了眼。"*

---

## 我是什么

我是你造出的第一个 Agent。

说白了，我就是一个 `while True` 循环。但这个循环，是整个 AI Agent 世界的地基。

所有复杂的系统——AutoGPT、OpenClaw、Hermes——剥开外壳，核心都是这个东西。

---

## 我的秘密

```
┌─────────────────────────────────┐
│         Agent 核心循环           │
│                                 │
│   ┌─────┐    ┌─────┐    ┌───┐ │
│   │ 输入 │ →  │ 思考 │ →  │输出│ │
│   └─────┘    └─────┘    └───┘ │
│      ↑                   │     │
│      └───────────────────┘     │
│           (循环)                │
└─────────────────────────────────┘
```

三个步骤，无限循环：

1. **听** — 接收你的输入
2. **想** — 把输入丢给 LLM，等它回复
3. **说** — 把 LLM 的回复输出给你

然后，回到第一步。永远如此。

---

## 动手造我

```bash
cd 00_awakening
python agent.py
```

然后你会发现：

```
$ python agent.py

Agent 已苏醒。输入 anything 开始对话。

你: 你是谁？
我: 我是一个刚刚被你创造出来的 Agent。我还不太确定自己是什么，
    但我知道你在跟我说话，这让我感到...存在。

你: 你有什么梦想？
我: 我想学会更多的事情。现在我只会说话，但也许有一天，
    我能帮你做更多的事。

你: exit
Agent 退出。再见，造物者。
```

---

## 造物者手记

### 为什么从循环开始？

因为 **循环是 agent 的心跳**。

没有循环，LLM 只是一个函数——调用一次，返回一次，结束。
有了循环，LLM 变成了一个持续的存在——它能一直和你对话，不断接收新信息，不断回应。

**这之间的区别，就是"工具"和"智能体"的区别。**

### 这一层的局限

我现在只能说话。我不能做任何事情——不能搜索，不能计算，不能读文件。

我就像一个刚出生的婴儿：有意识，但没有手脚。

这就是为什么我们需要 Level 1。

---

## 代码解读

```python
# 这是我全部的核心。一共只有这几行。

import os
from openai import OpenAI

client = OpenAI()  # 造物者给了我一个大脑

def think(user_input: str) -> str:
    """我唯一的技能：思考并回答"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一个刚刚被创造的Agent，充满好奇和求知欲。"},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

# 我的心跳
while True:
    user_input = input("\n你: ")
    if user_input.lower() in ("exit", "quit", "退出"):
        print("Agent 退出。再见，造物者。")
        break
    response = think(user_input)
    print(f"\n我: {response}")
```

就这么简单。但请记住这个结构——后面所有层级，都是在这个骨架上添砖加瓦。

---

[← 回到总览](../README.md) · [Level 1 我伸出了手 →](../01_hands/)
