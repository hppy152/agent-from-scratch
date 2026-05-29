# Level 6 · 我有了分身

> *"一个人能力再强，也做不了所有事。但如果我能创造出和我一样会思考的'分身'，让它们各司其职，我们就能完成更大的事情。"*

---

## SubAgent：动态分身术

Level 4 的多 Agent 是**静态团队**——搜索员、分析员、写作员，固定角色、固定职责。

Level 6 的 SubAgent 是**动态分身**——根据任务临时决定需要谁，需要几个就创造几个。

```
Level 4（静态）                 Level 6（动态）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Orchestrator               →  Orchestrator
  ├── 搜索员（固定）            ├── 根据任务动态创建 SubAgent
  ├── 分析员（固定）            │   "这个任务需要3个分身"
  └── 写作员（固定）            │   → 创建 3 个 SubAgent
                               │   → 各自独立工作
                               │   → 完成后销毁
```

---

## 核心机制：delegate_task

```python
# Orchestrator 的核心能力
response = orchestrator.delegate_task(
    agent_name="研究员",    # 分配给谁
    task="调研 Python 3.12 新特性"  # 做什么
)

# delegate_task 做了什么？
# 1. 找到名为"研究员"的 SubAgent
# 2. 创建独立的 LLM 会话（隔离上下文）
# 3. 把任务交给 SubAgent
# 4. SubAgent 独立执行 ReAct 循环
# 5. 完成后把结果返回给 Orchestrator
```

---

## 动手造我

```bash
cd 06_subagent
python agent.py
```

```
$ python agent.py

============================================================
  🪞 Agent v6.0 — 分身版
  已注册 3 个分身: 研究员, 分析师, 写手
  输入 'exit' 退出。
============================================================

你: 帮我调研一下 Rust 和 Python 哪个更适合写 Web 服务器

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 收到任务: 调研 Rust vs Python Web 服务器

📝 分发计划 (3 个子任务):
  1. 研究员: 调研 Rust Web 框架生态...
  2. 研究员: 调研 Python Web 框架生态...
  3. 分析师: 对比分析两种语言的 Web 开发体验...

⚡ 执行中...
    → 委派给 研究员: 调研 Rust Web 框架（Actix, Axum, Rocket）...
    ← 研究员 完成 (3步)
    → 委派给 研究员: 调研 Python Web 框架（Django, Flask, FastAPI）...
    ← 研究员 完成 (3步)
    → 委派给 分析师: 对比 Rust 和 Python 在 Web 开发中的优劣...
    ← 分析师 完成 (2步)

📊 综合结果...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent: 综合调研结果，以下是 Rust 和 Python 的 Web 服务器对比...
```

---

## 造物者手记

### 静态 vs 动态

| | Level 4（静态） | Level 6（动态） |
|--|----------------|----------------|
| 团队 | 预定义，固定 | 按需创建 |
| 上下文 | 共享或独立 | 完全隔离 |
| 扩展性 | 加新角色改代码 | 加新角色改 prompt |
| 适合 | 角色稳定的场景 | 任务多变的场景 |

### SubAgent 的隔离性

每个 SubAgent 有**独立的消息历史**。这意味着：

- SubAgent A 不知道 SubAgent B 在做什么
- 子 Agent 之间不共享上下文
- 父 Agent 是唯一的"信息中枢"

这种隔离是刻意的——防止子 Agent 之间互相干扰，也防止上下文窗口被无关信息塞满。

### 从 Level 6 到真实世界

```
你的实现                      生产级系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SubAgent                  →   Hermes SubAgent
delegate_task             →   delegate_task API
SubAgentOrchestrator      →   Orchestrator + Task Queue
独立上下文                 →   Session Isolation
动态创建/销毁              →   Worker Pool / Lambda
```

---

## 代码解读

### SubAgent：独立的思考者

```python
class SubAgent:
    def run(self, task: str) -> SubAgentResponse:
        """独立执行一个任务（完整的 ReAct 循环）"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        for step in range(self.max_steps):
            # 独立思考
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                # 独立行动
                for tc in msg.tool_calls:
                    result = self.tool_executor(tc.function.name, ...)
                    messages.append({"role": "tool", ...})
            else:
                # 任务完成，返回结果
                return SubAgentResponse(result=msg.content, ...)
```

### Orchestrator：调度中心

```python
class SubAgentOrchestrator:
    def delegate_task(self, agent_name: str, task: str):
        """核心：把任务委派给子 Agent"""

        # 1. 找到子 Agent
        agent = self.registered_agents[agent_name]

        # 2. 子 Agent 独立执行（父 Agent 等待）
        response = agent.run(task)

        # 3. 拿到结果
        return response  # result, tool_calls, steps
```

---

[← Level 5 我学会了连接世界](../05_connection/) · [回到总览](../README.md)
