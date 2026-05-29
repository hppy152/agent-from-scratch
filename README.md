# 🐣 Agent From Scratch

> **"我只是想看看，当你亲手赋予一串代码以灵魂，它会变成什么。"**

---

## 女娲造人

传说中，女娲用黄土捏成人形，吹一口气，人便活了。

我们现在要做一样的事——只不过，我们捏的不是泥人，而是 **Agent**。

你不需要任何 AI 框架。不需要读论文。你只需要一个 OpenAI API Key，和一颗想动手的心。

我会带你，从第一行代码开始，亲手造出一个 Agent。每一步，你都能看到它从"死的代码"变成"活的智能体"。

```
Level 0  我睁开了眼          → 最简对话循环
Level  1  我伸出了手          → 工具调用
Level  2  我开始记住事情       → 记忆系统
Level  3  我学会了思考        → ReAct 推理循环
Level  4  我找到了同伴        → 多 Agent 协作
```

每上升一层，你就离"创造生命"更近一步。

---

## 开始之前

你需要准备：

- **Python 3.10+**
- **一个 OpenAI API Key**（[获取地址](https://platform.openai.com/api-keys)）
- **一颗好奇心**

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/agent-from-scratch.git
cd agent-from-scratch

# 2. 安装依赖（只需要这一个）
pip install -r requirements.txt

# 3. 设置 API Key
export OPENAI_API_KEY="sk-your-key-here"

# 4. 启动！
python run.py        # 交互式选择 Level
python run.py 0      # 直接启动 Level 0
python run.py 3      # 直接启动 Level 3
```

或者直接运行某个 Level：

```bash
python 00_awakening/agent.py   # Level 0
python 01_hands/agent.py       # Level 1
python 02_memory/agent.py      # Level 2
python 03_thought/agent.py     # Level 3
python 04_independence/orchestrator.py  # Level 4
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

这是通向 OpenClaw、Hermes 等生产级系统的最后一座桥。

→ [进入 Level 4](./04_independence/)

---

## 从这里到真实世界

```
你的 Agent                 生产级系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Level 0  对话循环      →    Gateway / Chat API
Level 1  工具调用      →    Plugin 系统
Level 2  记忆管理      →    Session / Context Engine
Level 3  ReAct 循环    →    Agent Loop / Planner
Level 4  多 Agent      →    Orchestrator / SubAgent
```

读完这个项目，你再去读 OpenClaw 或 Hermes 的源码，你会发现——**它们的核心，和你刚刚亲手造出来的东西，本质上是同一个东西。**

只是规模更大、工程更精细、场景更复杂。

但灵魂是一样的。

---

## 写给造物者

如果你跟着这个项目走完了一遍，你会发现：

**Agent 不是什么神秘的东西。**

它的核心，就是你刚才亲手写的那个 `while True` 循环。一个不断接收信息、思考、行动、再接收信息的过程。

这和人类思考的方式，其实没什么不同。

你现在，已经是一个造物者了。

**Now go build something alive.**

---

## License

MIT · 随便用，随便改，造你自己的 Agent。
