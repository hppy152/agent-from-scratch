# Level 7 · 我会反思了

> *"以前失败了就失败了，我不会从中学习。但现在不一样了——每次跌倒，我都会想清楚为什么，然后站起来。下一次，我不会再犯同样的错。"*

---

## 什么是自我进化

自我进化 = **Agent 能从自己的经验中学习，变得越来越强。**

```
传统 Agent:
  任务 → 成功/失败 → 结束

自我进化 Agent:
  任务 → 成功 → 提取技能 → 存入技能库
  任务 → 失败 → 自我反思 → 存入反思记忆 → 下次改进
```

---

## 两个核心机制

### 1. Reflection（反思循环）

```
Agent 尝试任务
    ↓
失败了
    ↓
自我反思："我刚才错在哪？"
    ↓
"我应该先检查输入格式，而不是直接计算。"
    ↓
反思存入记忆
    ↓
下次遇到类似任务 → 回忆反思 → 避免重蹈覆辙
```

### 2. Skill Library（技能库）

```
Agent 成功完成任务
    ↓
自动提取"可复用技能"
    ↓
存入技能库（JSON 文件）
    ↓
下次类似任务 → 检索技能 → 直接复用
    ↓
技能库越来越大 → Agent 能力越来越强
```

---

## 动手造我

```bash
cd 07_evolution
python agent.py
```

```
$ python agent.py

============================================================
  🧬 Agent v7.0 — 自我进化版
  反思记录: 0 条 | 技能库: 0 个
  输入 'reflections' 查看反思，'skills' 查看技能库
============================================================

你: 帮我算一下 abc 的值
Agent: [思考] 这个任务需要数字计算...
  → 执行失败：输入不是有效数字
Agent: [反思] 任务失败了。原因：用户输入了非数字内容。
  → 建议：先验证输入是否为数字，再进行计算。
  → 已存入反思记忆。

你: 帮我算 3 的 5 次方
Agent: [回忆] 找到相关反思：先验证输入...
  → 检查：3 和 5 都是数字，可以计算
  → 计算结果：243
  → 成功！提取技能"幂运算计算"存入技能库。

你: reflections
  1. 任务: 帮我算 abc
     教训: 需要先验证输入格式
     建议: 先检查输入是否为数字

你: skills
  • 幂运算计算: 计算 a 的 b 次方 (步骤: 3)
```

---

## 造物者手记

### 为什么自我进化很重要？

没有自我进化的 Agent：每次都是"初生状态"，同样的错误会反复犯。

有自我进化的 Agent：经验会积累，能力会增长。就像人类——第一次骑自行车会摔跤，但摔几次之后就学会了。

### Reflexion 论文的核心洞察

> "LLM 可以用自然语言做自我强化学习。"

传统 RL 用数值 reward 更新权重。Reflexion 用自然语言描述错误和改进，存入记忆。效果出奇的好——在编程任务上，Reflexion 把成功率从 80% 提到了 91%。

### 和 Level 2 记忆的区别

| | Level 2 记忆 | Level 7 自我进化 |
|--|-------------|-----------------|
| 记什么 | 用户说的事实 | Agent 自己的经验教训 |
| 触发方式 | 用户说"记住" | 任务失败/成功时自动触发 |
| 用途 | 回答时参考 | 执行前预防 + 执行后提取技能 |

---

## 代码解读

### Reflection（反思循环）

```python
class ReflectionAgent:
    def execute_with_reflection(self, task):
        # 1. 带经验思考
        result = self.think(task)

        # 2. 失败则反思
        if is_failure(result):
            reflection = self.reflect_on_failure(task, result)
            # 反思自动存入记忆
            return {"success": False, "reflection": reflection}

        return {"success": True, "output": result}

    def think(self, task):
        # 3. 执行前回忆相关经验
        relevant = self.reflections.recall(task)
        prompt = f"历史经验：{relevant}\n\n当前任务：{task}"
        return self.llm_call(prompt)
```

### Skill Library（技能库）

```python
class SkillLibrary:
    def store(self, skill):
        """存储技能（同名技能会更新）"""
        self.skills.append(skill)
        self._save()  # 持久化到 JSON

    def retrieve(self, query, top_k=3):
        """检索相关技能"""
        # 按 trigger/name/description 匹配
        return sorted_skills[:top_k]

    def to_context(self, query):
        """检索技能并转为 prompt 上下文"""
        skills = self.retrieve(query)
        return "\n\n".join(s.to_prompt() for s in skills)
```

---

[← Level 6 我有了分身](../06_subagent/) · [Level 8 我会研究了 →](../08_research/)
