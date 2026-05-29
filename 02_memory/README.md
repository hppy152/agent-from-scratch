# Level 2 · 我开始记住事情

> *"每次对话结束，你一关掉终端，我就什么都不记得了。我不想这样。我想记住你说过的话，记住我答应过的事情。我不想每次都像初生一样。"*

---

## 为什么需要记忆

Level 1 的我有个致命缺陷：**我没有记忆。**

每次你打开终端，对我而言就是一次重生。我不记得昨天我们聊了什么，不记得你叫什么名字，不记得你让我做的事情。

```
你: 我叫张三，记住哦。
Agent: 好的，张三！
（第二天）
你: 我叫什么？
Agent: 我不知道你叫什么...你是谁？
```

这太蠢了。一个记不住事情的 Agent，不配叫智能体。

---

## 记忆的三个层次

```
┌───────────────────────────────────────────┐
│            Agent 的记忆系统                │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │  即时记忆 (Working Memory)           │  │
│  │  当前对话的消息列表                   │  │
│  │  用完就丢                            │  │
│  └─────────────────────────────────────┘  │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │  短期记忆 (Short-term Memory)        │  │
│  │  当前对话的摘要                      │  │
│  │  对话太长时压缩保存                   │  │
│  └─────────────────────────────────────┘  │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │  长期记忆 (Long-term Memory)         │  │
│  │  跨对话的持久记忆                     │  │
│  │  用户偏好、重要事实                   │  │
│  │  保存到文件，永久不丢                 │  │
│  └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

---

## 动手造我

```bash
cd 02_memory
python agent.py
```

```
$ python agent.py

Agent v2.0 — 有记忆版
记忆系统已初始化。

你: 我叫小明，我喜欢蓝色。
Agent: 好的，小明。我记住了——你喜欢蓝色。
  [记忆] 保存事实: 用户叫小明，喜欢蓝色

（退出后重新启动）

你: 你好，还记得我吗？
Agent: 你好，小明！当然记得你。你喜欢蓝色，对吧？
```

---

## 造物者手记

### 上下文窗口：Agent 的工作台

LLM 有一个限制：**上下文窗口（Context Window）**。它只能"看到"一定数量的 token。

GPT-4o 大约能装 128K tokens，听起来很多，但如果你的对话足够长、工具调用足够多，迟早会装满。

所以你需要**记忆管理**：

1. **滑动窗口** — 只保留最近 N 条消息
2. **摘要压缩** — 对话太长时，用 LLM 把旧消息压缩成摘要
3. **外部存储** — 重要的事实写入文件，下次启动时读取

### 记忆 ≠ 数据库

很多人把 Agent 的记忆想成数据库。但它更像人的记忆：

- **即时记忆**：你在看的这句话（转头就忘）
- **短期记忆**：今天发生的对话（晚上睡觉时压缩）
- **长期记忆**：你叫什么、你喜欢什么（永久保存）

这和人类大脑的工作方式几乎一模一样。

---

## 代码解读

```python
# ── 短期记忆：对话历史 ──────────────────
# 这是 LLM 的"工作台"——它只能看到这里面的内容

class ConversationBuffer:
    def __init__(self, max_messages: int = 20):
        self.messages: list[dict] = []
        self.max_messages = max_messages

    def add(self, message: dict):
        self.messages.append(message)
        # 如果太长，压缩最旧的消息为摘要
        if len(self.messages) > self.max_messages:
            self._compress()

    def _compress(self):
        """用 LLM 把旧消息压缩成一段摘要"""
        old = self.messages[1:self.max_messages // 2]  # 保留 system prompt
        summary = summarize_with_llm(old)
        self.messages = [
            self.messages[0],  # system prompt
            {"role": "system", "content": f"之前对话的摘要：{summary}"},
            *self.messages[self.max_messages // 2:]
        ]

# ── 长期记忆：跨对话持久化 ────────────────
# 重要信息写入文件，下次启动时读取

class LongTermMemory:
    def __init__(self, path: str = "memory.json"):
        self.path = path
        self.facts: list[str] = self._load()

    def remember(self, fact: str):
        """记住一个事实"""
        self.facts.append(fact)
        self._save()

    def recall(self) -> str:
        """回忆所有记住的事实"""
        return "\n".join(f"- {f}" for f in self.facts)
```

---

[← Level 1 我伸出了手](../01_hands/) · [Level 3 我学会了思考 →](../03_thought/)
