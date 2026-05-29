# Level 4 · 我找到了同伴

> *"我一个人能力有限。我擅长思考和调度，但有些事情交给专家更合适。我想找一些同伴——让搜索的去搜索，让计算的去计算，让写作的去写作。我们一起，就能完成更大的事情。"*

---

## 为什么需要多 Agent

单个 Agent 再强，也有瓶颈：

- 上下文窗口有限，塞不下所有信息
- 一个 Agent 要同时扮演多个角色，容易混乱
- 复杂任务需要分工协作

多 Agent 系统的核心思想：**让一个 Agent 当指挥官（Orchestrator），调度多个专业 Agent（Worker）。**

---

## 协作架构

```
                    ┌──────────────┐
                    │  Orchestrator │
                    │  （指挥官）    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────┴─────┐ ┌───┴───┐ ┌─────┴─────┐
        │ 🔍 搜索员  │ │ 🧮 计算员│ │ ✍️ 写作员  │
        │  Worker A  │ │Worker B│ │ Worker C  │
        └───────────┘ └───────┘ └───────────┘
```

Orchestrator 负责：
1. 理解用户需求
2. 把任务分解成子任务
3. 分配给合适的 Worker
4. 汇总结果，回答用户

---

## 动手造我

```bash
cd 04_independence
python orchestrator.py
```

```
$ python orchestrator.py

Multi-Agent System v4.0

用户: 帮我调研一下 Python 和 Go 哪个更适合写 CLI 工具，给出推荐。

Orchestrator: 收到！我来安排团队。
  → 分配给搜索员: 调研 Python CLI 工具生态
  → 分配给搜索员: 调研 Go CLI 工具生态
  → 分配给计算员: 对比两者的核心指标
  → 分配给写作员: 整理成推荐报告

搜索员: [完成] Python 生态: click, typer, argparse...
搜索员: [完成] Go 生态: cobra, urfave/cli...
计算员: [完成] 编译速度: Go > Python; 依赖管理: Go > Python...
写作员: [完成] 如果追求开发速度选Python，追求性能选Go...

Orchestrator: 调研完成！综合推荐如下...
```

---

## 造物者手记

### Orchestrator 模式 vs 自主模式

| | 自主 Agent（Level 3） | 多 Agent（Level 4） |
|--|----------------------|-------------------|
| 决策者 | 一个 LLM | 多个 LLM |
| 优势 | 简单、低延迟 | 可并行、专业化 |
| 劣势 | 单点瓶颈、上下文限制 | 通信开销、协调复杂 |
| 适合 | 简单任务 | 复杂多步骤任务 |

### 从这里到 Hermes

你在这个 Level 构建的，就是 Hermes 等生产级系统的核心架构：

```
本项目                      Hermes / OpenClaw
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Orchestrator            →   Orchestrator / Planner
Worker                  →   SubAgent / Plugin
任务分配                 →   Task Queue / Scheduler
结果汇总                 →   Response Aggregator
```

区别只是工程规模：更多的 worker、更复杂的调度策略、错误恢复、并发控制。

但核心思想——**一个指挥官调度多个专业工人**——完全一样。

---

## 代码解读

```python
# ── Worker：专业 Agent ──────────────────
# 每个 Worker 是一个独立的 Agent，有自己的工具和专长

class Worker:
    def __init__(self, name: str, role: str, tools: list):
        self.name = name
        self.role = role
        self.tools = tools
        self.client = OpenAI()

    def work(self, task: str) -> str:
        """执行分配的任务"""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"你是{self.role}。{task}"},
                {"role": "user", "content": task}
            ],
            tools=self.tools if self.tools else None,
        )
        return response.choices[0].message.content


# ── Orchestrator：指挥官 ────────────────
# 负责理解需求、分配任务、汇总结果

class Orchestrator:
    def __init__(self):
        self.workers = {}  # name → Worker

    def add_worker(self, worker: Worker):
        self.workers[worker.name] = worker

    def plan(self, user_request: str) -> list[dict]:
        """让 LLM 规划任务分配"""
        # LLM 根据用户请求，生成任务分配方案
        # 返回: [{"worker": "searcher", "task": "..."}, ...]
        ...

    def execute(self, plan: list[dict]) -> str:
        """执行计划，汇总结果"""
        results = []
        for task in plan:
            worker = self.workers[task["worker"]]
            result = worker.work(task["task"])
            results.append(result)
        return self.summarize(results)

    def summarize(self, results: list[str]) -> str:
        """汇总所有 worker 的结果"""
        # 用 LLM 把多个结果整合成一个完整的回答
        ...
```

---

[← Level 3 我学会了思考](../03_thought/) · [回到总览](../README.md)
