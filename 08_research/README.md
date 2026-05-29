# Level 8 · 我会研究了

> *"以前你问我一个问题，我只能凭我知道的回答。但现在不一样了——我能自己去调研，分解问题，搜索信息，交叉验证，最后给你一份有依据的研究报告。"*

---

## 什么是深度研究

深度研究 = **Agent 像人类研究员一样，自主进行多步调研。**

```
用户: "Rust 和 Go 哪个更适合写 Web 服务器？"

普通 Agent:
  → 凭训练数据回答（可能过时、不准确）

深度研究 Agent:
  1. 分解问题 → 4 个子问题
  2. 逐个调研 → 搜索真实信息
  3. 交叉验证 → 多源比对
  4. 综合报告 → 有依据的结论
```

---

## 研究流程

```
                    ┌──────────────┐
  用户问题 ──────→ │  分解器       │
                    │ Decomposer   │
                    └──────┬───────┘
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
         子问题1       子问题2       子问题3
              ↓            ↓            ↓
         ┌────────┐  ┌────────┐  ┌────────┐
         │调研员A  │  │调研员B  │  │调研员C  │
         │搜索+分析│  │搜索+分析│  │搜索+分析│
         └────┬───┘  └────┬───┘  └────┬───┘
              ↓            ↓            ↓
              └────────────┼────────────┘
                           ↓
                    ┌──────────────┐
                    │  综合器       │
                    │ Synthesizer  │
                    └──────┬───────┘
                           ↓
                    最终研究报告
```

---

## 动手造我

```bash
cd 08_research
python agent.py
```

```
$ python agent.py

============================================================
  🔬 Agent v8.0 — 深度研究版
  输入 'exit' 退出。
============================================================

你: Rust 和 Go 哪个更适合写 Web 服务器？

🔬 开始深度研究...

📋 分解问题 (4 个子问题):
  1. Rust Web 框架有哪些？各自特点？
  2. Go Web 框架有哪些？各自特点？
  3. Rust vs Go Web 性能对比
  4. Rust vs Go 开发体验对比

🔍 调研中...
  → 子问题 1 完成
  → 子问题 2 完成
  → 子问题 3 完成
  → 子问题 4 完成

📊 综合报告...

Agent: # Rust vs Go Web 服务器研究报告

## 概述
Rust 和 Go 都是现代 Web 服务器的优秀选择...

## 详细分析
### Rust Web 框架
- Actix Web: 高性能，异步...
- Axum: Tokio 团队出品...

### Go Web 框架
- Gin: 高性能，简洁...
- Echo: 丰富的中间件...

## 结论
- 追求极致性能选 Rust
- 追求开发效率选 Go
```

---

## 造物者手记

### 研究型 Agent 的关键能力

1. **问题分解**：大问题拆成小问题
2. **信息检索**：搜索真实信息（不是编造）
3. **交叉验证**：多源比对，确保准确性
4. **综合分析**：把碎片信息整合成结构化报告

### 和普通搜索的区别

| | 普通搜索 | 深度研究 |
|--|---------|---------|
| 问题 | 一个搜索词 | 一个复杂问题 |
| 过程 | 搜一次就完 | 分解 → 多次搜索 → 验证 → 综合 |
| 结果 | 原始链接列表 | 结构化研究报告 |
| 质量 | 可能不相关 | 经过筛选和验证 |

### 代表项目

- **GPT Researcher**（18k⭐）：自主调研 + 多源验证
- **STORM**（10k⭐）：斯坦福出品，模拟维基百科写作
- **Perplexity**：对话式深度搜索（商业产品）

---

## 代码解读

### 问题分解器

```python
class QuestionDecomposer:
    def decompose(self, question, max_sub_questions=5):
        # 让 LLM 把问题拆成子问题
        response = llm.chat(f"把这个问题拆成子问题：{question}")
        return parsed["sub_questions"]
```

### 调研员

```python
class Investigator:
    def investigate(self, sub_question):
        # ReAct 循环：搜索 → 分析 → 结论
        for step in range(max_steps):
            if needs_search:
                result = search(sub_question)
            else:
                return findings
```

### 综合器

```python
class Synthesizer:
    def synthesize(self, question, investigations):
        # 把多个调研结果整合成报告
        return llm.chat(f"综合以下调研：{investigations}")
```

---

[← Level 7 我会反思了](../07_evolution/) · [回到总览](../README.md)
