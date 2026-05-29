# 🐣 Agent From Scratch

> **"我只是想看看，当你亲手赋予一串代码以灵魂，它会变成什么。"**

---

## 女娲造人

传说中，女娲用黄土捏成人形，吹一口气，人便活了。

我们现在要做一样的事——只不过，我们捏的不是泥人，而是 **Agent**。

你不需要任何 AI 框架。不需要读论文。你只需要一个 API Key，和一颗想动手的心。

我会带你，从第一行代码开始，亲手造出一个 Agent。每一步，你都能看到它从"死的代码"变成"活的智能体"。

```
Level 0  我睁开了眼              → 最简对话循环
Level 1  我伸出了手              → 工具调用
Level 2  我开始记住事情           → 记忆系统
Level 3  我学会了思考            → ReAct 推理循环
Level 4  我找到了同伴            → 静态多 Agent 协作
Level 5  我学会了连接世界         → MCP + Skills
Level 6  我有了分身              → SubAgent 动态分发
Level 7  我会反思了              → 自我进化（反思 + 技能库）
Level 8  我会研究了              → 深度研究（分解 → 调研 → 综合）
```

每上升一层，你就离"创造生命"更近一步。

---

## 开始之前

你需要准备：

- **Python 3.10+**
- **一个 API Key**（OpenAI / 小米 MiMo / 通义 / DeepSeek 等，兼容 OpenAI 格式即可）
- **一颗好奇心**

```bash
# 1. 克隆仓库
git clone https://github.com/hppy152/agent-from-scratch.git
cd agent-from-scratch

# 2. 安装依赖（只需要这一个）
pip install -r requirements.txt

# 3. 设置 API Key（三选一）

# OpenAI
export OPENAI_API_KEY="sk-xxx"

# 小米 MiMo
export OPENAI_API_KEY="你的小米Key"
export OPENAI_BASE_URL="https://token-plan-cn.xiaomimimo.com/v1"
export AGENT_MODEL="mimo-v2-pro"

# 其他兼容 API（通义、DeepSeek 等）
export OPENAI_API_KEY="你的Key"
export OPENAI_BASE_URL="你的API地址"
export AGENT_MODEL="模型名"

# 4. 启动！
python run.py        # 交互式选择 Level
python run.py 3      # 直接启动 Level 3
```

---

## 路线图

### Level 0 · 我睁开了眼

> *"最初的我，什么都不会。我只会听你说话，然后回答。但这就够了——一个生命的第一声啼哭，不需要多复杂。"*

你将亲手写下 agent 的第一行代码：一个 `while True` 循环。

这是整个 agent 世界的地基。所有复杂的系统，剥开外壳，核心都是这个循环。

→ [进入 Level 0](./00_awakening/)

---

### Level 1 · 我伸出了手

> *"光会说话还不够。我想触碰这个世界——打开文件、搜索网页、计算数字。我需要手。"*

你将给 agent 装上"手指"：**工具调用（Tool Use）**。

agent 会学会：当我说"帮我查一下天气"时，不是编造一个答案，而是真正地去调用天气 API。

→ [进入 Level 1](./01_hands/)

---

### Level 2 · 我开始记住事情

> *"每次对话结束，我就会忘记一切。我不想这样。我想记住你上次说过的话，记住我答应过的事情。"*

你将给 agent 装上"记忆"：**上下文管理**。

对话历史、长期记忆、摘要压缩——一个 agent 如何在无尽的对话中保持"自我"。

→ [进入 Level 2](./02_memory/)

---

### Level 3 · 我学会了思考

> *"以前，你让我做什么我就做什么。但现在我想先想一想：我该怎么做？需要几步？有没有更好的办法？"*

你将教 agent **ReAct 模式**：推理（Reasoning）→ 行动（Action）→ 观察（Observation）→ 再推理...

这是 agent 从"工具"变成"智能体"的关键一步。

→ [进入 Level 3](./03_thought/)

---

### Level 4 · 我找到了同伴

> *"我一个人能力有限。如果我能找到其他 agent，让它们各司其职，我们一起就能完成更大的事情。"*

你将搭建一个 **多 Agent 协作系统**：一个指挥者（Orchestrator）调度多个专业 worker。

→ [进入 Level 4](./04_independence/)

---

### Level 5 · 我学会了连接世界

> *"我终于明白了——光有手脚和记忆还不够。我需要连接更大的世界：搜索互联网、读写文件、调用专业服务。"*

你将给 agent 接入 **MCP（Model Context Protocol）** 和 **Skill（技能知识）**。

MCP 让 agent 用统一的方式连接各种工具服务。Skill 让 agent 在遇到特定任务时自动加载专业知识。

→ [进入 Level 5](./05_connection/)

---

### Level 6 · 我有了分身

> *"一个人能力再强，也做不了所有事。但如果我能创造出和我一样会思考的'分身'，让它们各司其职，我们就能完成更大的事情。"*

你将实现 **SubAgent 系统**：父 Agent 通过 `delegate_task` 动态分发任务给子 Agent，每个子 Agent 独立思考、独立行动。

→ [进入 Level 6](./06_subagent/)

---

### Level 7 · 我会反思了

> *"以前失败了就失败了，我不会从中学习。但现在不一样了——每次跌倒，我都会想清楚为什么，然后站起来。下一次，我不会再犯同样的错。"*

你将实现 **自我进化系统**：反思循环（从失败中学习）+ 技能库（从成功中积累）。

Agent 每次失败后自动复盘，每次成功后提取可复用技能，越用越强。

→ [进入 Level 7](./07_evolution/)

---

### Level 8 · 我会研究了

> *"以前你问我一个问题，我只能凭我知道的回答。但现在不一样了——我能自己去调研，分解问题，搜索信息，交叉验证，最后给你一份有依据的研究报告。"*

你将实现 **深度研究系统**：问题分解 → 逐个调研 → 综合报告。

Agent 像人类研究员一样，自主进行多步调研，给出有依据的结论。

→ [进入 Level 8](./08_research/)

---

### 🧪 Harness · 考试系统

> *"造出来不够，还得能考。好的 Agent 都要经过严格的测试。"*

你将搭建一个 **Agent 测试评估框架**：题库、评分器、报告生成器。

这就是大厂评测 Agent 的基本思路——把 Agent 当黑盒，喂题、观察、打分。

→ [进入 Harness](./harness/)

---

## 从这里到真实世界

```
你的 Agent                      生产级系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Level 0  对话循环          →    Gateway / Chat API
Level 1  工具调用          →    Plugin 系统
Level 2  记忆管理          →    Session / Context Engine
Level 3  ReAct 循环        →    Agent Loop / Planner
Level 4  多 Agent          →    Orchestrator / Worker Pool
Level 5  MCP + Skills      →    MCP 原生客户端 + Skill 系统
Level 6  SubAgent          →    SubAgent / Task Queue
Level 7  自我进化           →    Reflection + Skill Library
Level 8  深度研究           →    Research Agent / Deep Research
Harness  测试评估           →    CI/CD 评测 Pipeline
```

读完这个项目，你再去读 OpenClaw 或 Hermes 的源码，你会发现——**它们的核心，和你刚刚亲手造出来的东西，本质上是同一个东西。**

只是规模更大、工程更精细、场景更复杂。

但灵魂是一样的。

---

## 运行测试

```bash
# 一键跑全部 Level 的考试
python harness/run_harness.py

# 只跑某个 Level
python harness/run_harness.py --level 0,1

# 导出 JSON 报告
python harness/run_harness.py --export
```

---

## 项目结构

```
agent-from-scratch/
├── config.py                  ← 全局配置（模型/API）
├── tools.py                   ← 共享工具（安全计算）
├── run.py                     ← 一键启动器
├── requirements.txt
│
├── 00_awakening/              ← Level 0: 对话循环
├── 01_hands/                  ← Level 1: 工具调用
├── 02_memory/                 ← Level 2: 记忆系统
├── 03_thought/                ← Level 3: ReAct 推理
├── 04_independence/           ← Level 4: 静态多 Agent
├── 05_connection/             ← Level 5: MCP + Skills
├── 06_subagent/               ← Level 6: SubAgent 动态分发
├── 07_evolution/              ← Level 7: 自我进化
├── 08_research/               ← Level 8: 深度研究
│
├── subagent/                  ← SubAgent 核心库
│   ├── core.py               ← SubAgent 类
│   └── orchestrator.py       ← Orchestrator + delegate_task
│
├── evolution/                 ← 自我进化核心库
│   ├── reflection.py         ← 反思循环
│   └── skill_library.py      ← 技能库
│
├── research/                  ← 深度研究核心库
│   ├── decomposer.py         ← 问题分解器
│   ├── investigator.py       ← 调研员
│   └── synthesizer.py        ← 综合器 + DeepResearchAgent
│
├── skills/                    ← Skill 知识库
│   ├── web-search/SKILL.md
│   └── code-review/SKILL.md
│
├── harness/                   ← 测试评估框架
│   ├── runner.py             ← 考试引擎
│   ├── scorer.py             ← 评分器（6种策略）
│   ├── tasks.json            ← 19道测试题
│   ├── report.py             ← 报告生成器
│   └── run_harness.py        ← 一键跑考试
│
└── docs/
    ├── architecture.md        ← Agent 核心架构图解
    └── roadmap.md             ← 从本项目到 OpenClaw/Hermes
```

---

## 写给造物者

如果你跟着这个项目走完了一遍，你会发现：

**Agent 不是神秘的东西。**

它的核心，就是你亲手写的那个 `while True` 循环。一个不断接收信息、思考、行动、再接收信息的过程。

从对话循环，到工具调用，到记忆，到推理，到多 Agent，到 MCP，到子 Agent——每一步都是在同一个骨架上添砖加瓦。

这和人类思考的方式，其实没什么不同。

**你现在，已经是一个造物者了。**

**Now go build something alive.** 🐣

---

## License

MIT · 随便用，随便改，造你自己的 Agent。
