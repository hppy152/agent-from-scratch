# Level 5 · 我学会了连接世界

> *"我终于明白了——光有手脚和记忆还不够。我需要连接更大的世界：搜索互联网、读写文件、调用专业服务。我需要一个标准的接口，让我能接入任何工具。"*

---

## MCP：给 Agent 一个标准化的手

**MCP (Model Context Protocol)** 是一个开放协议，让 Agent 能用统一的方式连接各种工具服务。

```
你的 Agent
    │
    ├── MCP Server A（文件系统）→ 读写文件
    ├── MCP Server B（搜索引擎）→ 搜索网页
    ├── MCP Server C（数据库）  → 查询数据
    └── MCP Server D（你的自定义服务）→ 任何能力
```

每个 MCP Server 就像一个"即插即用"的工具包。你不需要为每个工具写适配代码——只要它支持 MCP 协议，你的 Agent 就能直接使用。

---

## Skill：给 Agent 加载知识

**Skill** 是一份 Markdown 文档，告诉 Agent "遇到某类任务时，按这个流程做"。

```
skills/
  web-search/SKILL.md     ← 搜索策略和注意事项
  code-review/SKILL.md    ← 代码审查维度和输出格式
  data-analysis/SKILL.md  ← 数据分析流程
```

当用户问"帮我搜一下"时，Agent 自动加载 web-search skill，获得搜索的最佳实践。

---

## 动手造我

```bash
cd 05_connection

# 1. 先测试 MCP Server 能不能跑
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python simple_mcp_server.py

# 2. 运行完整 Agent
python agent.py
```

```
$ python agent.py

============================================================
  🌍 Agent v5.0 — 连接世界版
  已加载 2 个技能: web-search, code-review
  已连接 1 个 MCP Server: simple-mcp-server
  可用 MCP 工具: calculate, get_weather, web_search, get_time
============================================================

你: 帮我搜一下 Python 3.12 有什么新特性

[Skill] 匹配: web-search
  → 加载搜索技能知识
  → 调用 MCP: web_search(query="Python 3.12 新特性")
  → 返回结果

Agent: 根据搜索结果，Python 3.12 的主要新特性包括：
1. 更好的错误提示...
2. f-string 改进...
3. ...

你: exit
Agent: 再见，造物者。世界很大，我已经准备好了。
```

---

## 造物者手记

### MCP 的本质

MCP 不是什么复杂的东西。它就是：

1. **启动一个子进程**（MCP Server）
2. **通过 stdin/stdout 发 JSON**（JSON-RPC 2.0）
3. **问它有什么工具**（tools/list）
4. **调用工具**（tools/call）

就这么简单。整个 MCP Client 不到 100 行代码。

### Skill vs Tool

| | Skill | Tool |
|--|-------|------|
| 是什么 | 知识（markdown） | 能力（代码） |
| 何时加载 | 用户提问时匹配 | Agent 启动时注册 |
| 作用 | 告诉 Agent "怎么做" | 让 Agent "能做什么" |
| 例子 | 搜索策略、审查规范 | 计算器、天气 API |

**Skill 是大脑里的知识，Tool 是手上的工具。**

### 从 Level 5 到真实世界

```
你的实现                     生产级系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MCP Client               →   Hermes MCP 原生客户端
MCP Server (stdio)       →   MCP Server (HTTP/SSE)
Skill Loader             →   Hermes Skill 系统
SKILL.md (frontmatter)   →   SKILL.md (完整规范)
```

---

## 代码解读

### MCP 通信流程

```
Client                          Server
  │                                │
  │──── initialize ──────────────→│  "你好，我是 Agent"
  │←─── capabilities ─────────────│  "你好，我有这些工具"
  │                                │
  │──── notifications/initialized ─│  "初始化完成"
  │                                │
  │──── tools/list ──────────────→│  "给我看看你的工具"
  │←─── tools[] ─────────────────│  "这是我的工具清单"
  │                                │
  │──── tools/call ──────────────→│  "帮我算 1+1"
  │←─── result ──────────────────│  "结果是 2"
  │                                │
  │─── ... 继续对话 ... ─────────│
```

### Skill 匹配逻辑

```python
# 当用户说: "帮我搜一下 Python 新特性"
# Skill Loader 会：

# 1. 扫描 skills/ 目录
skills = ["web-search", "code-review"]

# 2. 匹配关键词
"web-search" 的 tags: [搜索, search, 查找]
"搜索" 出现在用户输入中 → 得分 +3

"code-review" 的 tags: [代码, code, review]
没有匹配 → 得分 0

# 3. 加载得分最高的 skill
→ 加载 web-search 的 SKILL.md 内容

# 4. 注入 system prompt
system_prompt += skill.content
```

---

[← Level 4 我找到了同伴](../04_independence/) · [回到总览](../README.md)
