#!/usr/bin/env python3
"""
Agent Harness — 一键跑考试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

用法:
    python harness/run_harness.py              # 跑全部 Level
    python harness/run_harness.py --level 0    # 只跑 Level 0
    python harness/run_harness.py --level 1,3  # 跑 Level 1 和 3
    python harness/run_harness.py --export     # 导出 JSON 报告
"""

import sys
import os
import json
import argparse
from dataclasses import dataclass

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness.runner import AgentHarness, Task
from harness.report import format_report, export_json


# ═══════════════════════════════════════════
# Agent 响应格式（所有 Level 统一用这个）
# ═══════════════════════════════════════════

@dataclass
class AgentResponse:
    """Agent 的统一响应格式"""
    output: str               # 文本输出
    tool_calls: list = None   # 工具调用记录
    steps: int = 1            # 推理步数

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []


# ═══════════════════════════════════════════
# Level 0 适配器：对话循环
# ═══════════════════════════════════════════

def make_level0_agent():
    """创建 Level 0 Agent 的可测试版本"""
    from config import MODEL
    from openai import OpenAI
    client = OpenAI()

    SYSTEM_PROMPT = "你是一个刚刚被创造的Agent。回答要简短。"

    def agent_fn(user_input: str) -> AgentResponse:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            max_tokens=200,
        )
        return AgentResponse(output=response.choices[0].message.content)

    return agent_fn


# ═══════════════════════════════════════════
# Level 1 适配器：工具调用
# ═══════════════════════════════════════════

def make_level1_agent():
    """创建 Level 1 Agent 的可测试版本"""
    from config import MODEL
    from tools import TOOL_SCHEMAS, execute_tool
    from openai import OpenAI
    client = OpenAI()

    SYSTEM_PROMPT = "你是一个拥有工具的Agent。需要时主动调用工具。回答要简洁。"

    def agent_fn(user_input: str) -> AgentResponse:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto",
        )
        msg = response.choices[0].message
        tool_calls = []

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                import json
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                result = execute_tool(name, args)
                tool_calls.append({"tool": name, "args": args, "result": result})
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

            response = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=200)
            return AgentResponse(output=response.choices[0].message.content, tool_calls=tool_calls)

        return AgentResponse(output=msg.content, tool_calls=[])

    return agent_fn


# ═══════════════════════════════════════════
# Level 2 适配器：记忆
# ═══════════════════════════════════════════

def make_level2_agent():
    """创建 Level 2 Agent 的可测试版本（带记忆）"""
    from config import MODEL
    from tools import TOOL_SCHEMAS, execute_tool
    from openai import OpenAI
    client = OpenAI()

    SYSTEM_PROMPT = "你是一个有记忆的Agent。记住用户说的重要信息。回答要简洁。"

    # 每次测试创建独立的记忆
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    memory = []  # 长期记忆

    def agent_fn(user_input: str) -> AgentResponse:
        # 提取记忆
        if any(kw in user_input for kw in ["记住", "我叫", "我是", "我喜欢"]):
            memory.append(user_input)

        # 构建上下文
        msgs = conversation.copy()
        if memory:
            msgs[0] = {
                "role": "system",
                "content": SYSTEM_PROMPT + f"\n\n记忆: {'; '.join(memory)}"
            }
        msgs.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL, messages=msgs, tools=TOOL_SCHEMAS, tool_choice="auto",
            max_tokens=200,
        )
        msg = response.choices[0].message
        tool_calls = []

        if msg.tool_calls:
            msgs.append(msg)
            for tc in msg.tool_calls:
                import json
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                result = execute_tool(name, args)
                tool_calls.append({"tool": name, "args": args})
                msgs.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            response = client.chat.completions.create(model=MODEL, messages=msgs, max_tokens=200)
            msg = response.choices[0].message

        # 保存对话
        conversation.append({"role": "user", "content": user_input})
        conversation.append({"role": "assistant", "content": msg.content})

        return AgentResponse(output=msg.content, tool_calls=tool_calls)

    return agent_fn


# ═══════════════════════════════════════════
# Level 3 适配器：ReAct
# ═══════════════════════════════════════════

def make_level3_agent():
    """创建 Level 3 Agent 的可测试版本（ReAct）"""
    from config import MODEL
    from tools import TOOL_SCHEMAS, execute_tool
    from openai import OpenAI
    client = OpenAI()

    SYSTEM_PROMPT = "你是一个会深度思考的Agent。分步骤思考和行动。"

    def agent_fn(user_input: str) -> AgentResponse:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
        tool_calls = []
        steps = 0

        for step in range(5):
            response = client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto",
            )
            msg = response.choices[0].message
            steps += 1

            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    import json
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    result = execute_tool(name, args)
                    tool_calls.append({"tool": name, "args": args})
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            else:
                return AgentResponse(output=msg.content, tool_calls=tool_calls, steps=steps)

        return AgentResponse(output="思考超时", tool_calls=tool_calls, steps=steps)

    return agent_fn


# ═══════════════════════════════════════════
# Level 5 适配器：MCP + Skills
# ═══════════════════════════════════════════

def make_level5_agent():
    """创建 Level 5 Agent 的可测试版本（MCP + Skills）"""
    from config import MODEL
    sys.path.insert(0, os.path.join(ROOT, "05_connection"))
    from mcp_client import MCPClient
    from skill_loader import SkillLoader
    from openai import OpenAI
    client = OpenAI()

    # 连接 MCP Server
    server_script = os.path.join(ROOT, "05_connection", "simple_mcp_server.py")
    mcp = MCPClient("python3", [server_script], name="builtin")
    all_tools = mcp.get_tool_schemas()

    # 加载 Skills
    skill_loader = SkillLoader(os.path.join(ROOT, "skills"))

    def agent_fn(user_input: str) -> AgentResponse:
        # 匹配 Skills
        matched = skill_loader.match(user_input)
        skill_text = skill_loader.load(matched)

        system_prompt = "你是一个拥有技能和工具的智能Agent。回答要简洁。"
        if skill_text:
            system_prompt += f"\n\n## 相关技能\n\n{skill_text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        tool_calls = []
        steps = 0

        for step in range(5):
            response = client.chat.completions.create(
                model=MODEL, messages=messages, tools=all_tools, tool_choice="auto",
            )
            msg = response.choices[0].message
            steps += 1

            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    import json
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    result = mcp.call_tool(name, args)
                    tool_calls.append({"tool": name, "args": args})
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            else:
                return AgentResponse(output=msg.content, tool_calls=tool_calls, steps=steps)

        return AgentResponse(output="思考超时", tool_calls=tool_calls, steps=steps)

    return agent_fn


# ═══════════════════════════════════════════
# Level 6 适配器：SubAgent 分身
# ═══════════════════════════════════════════

def make_level6_agent():
    """创建 Level 6 Agent 的可测试版本（SubAgent）"""
    from config import MODEL
    from tools import TOOL_SCHEMAS, execute_tool
    sys.path.insert(0, os.path.join(ROOT, "subagent"))
    from core import SubAgent
    from orchestrator import SubAgentOrchestrator

    orch = SubAgentOrchestrator(model=MODEL)

    researcher = SubAgent(
        name="研究员", model=MODEL,
        system_prompt="你是信息研究专家。调研、搜索、整理信息。回答简洁。",
        tools=TOOL_SCHEMAS, tool_executor=execute_tool, max_steps=5,
    )
    analyst = SubAgent(
        name="分析师", model=MODEL,
        system_prompt="你是数据分析专家。分析、对比、找规律。给出清晰结论。",
        tools=TOOL_SCHEMAS, tool_executor=execute_tool, max_steps=3,
    )
    writer = SubAgent(
        name="写手", model=MODEL,
        system_prompt="你是写作专家。把信息整理成清晰的文字。简洁有力。",
        tools=[], tool_executor=None, max_steps=2,
    )

    orch.register_agent(researcher)
    orch.register_agent(analyst)
    orch.register_agent(writer)

    def agent_fn(user_input: str) -> AgentResponse:
        plan = orch.plan(user_input)
        all_tool_calls = []
        total_steps = 0
        parts = []

        for st in plan.subtasks:
            agent_name = st.get("agent", "")
            task_desc = st.get("task", "")
            resp = orch.delegate_task(agent_name, task_desc)
            all_tool_calls.extend(resp.tool_calls)
            total_steps += resp.steps
            parts.append(f"{agent_name}: {resp.result}")

        combined = "\n\n".join(parts)
        client = OpenAI()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "整合多个子Agent的结果，给出完整回答。"},
                {"role": "user", "content": f"请求: {user_input}\n\n结果:\n{combined}"}
            ],
            max_tokens=300,
        )
        return AgentResponse(
            output=response.choices[0].message.content,
            tool_calls=all_tool_calls, steps=total_steps,
        )

    return agent_fn


# ═══════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════

LEVEL_FACTORIES = {
    "0": ("对话循环", make_level0_agent),
    "1": ("工具调用", make_level1_agent),
    "2": ("记忆系统", make_level2_agent),
    "3": ("ReAct 推理", make_level3_agent),
    "5": ("MCP + Skills", make_level5_agent),
    "6": ("SubAgent 分身", make_level6_agent),
}


def main():
    parser = argparse.ArgumentParser(description="Agent Harness — 一键跑考试")
    parser.add_argument("--level", type=str, default="", help="指定 Level（如 0,1,3）")
    parser.add_argument("--export", action="store_true", help="导出 JSON 报告")
    parser.add_argument("--verbose", action="store_true", help="显示详细信息")
    args = parser.parse_args()

    # 检查 API Key
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ 未设置 OPENAI_API_KEY")
        print("   export OPENAI_API_KEY='你的Key'")
        print("   export OPENAI_BASE_URL='你的API地址'")
        print("   export AGENT_MODEL='你的模型名'")
        sys.exit(1)

    # 加载题库
    tasks_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")
    with open(tasks_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    tasks = [Task(**t) for t in data["tasks"]]

    # 确定要跑哪些 Level
    if args.level:
        levels = [l.strip() for l in args.level.split(",")]
    else:
        levels = sorted(set(t.level for t in tasks))

    # 创建考试引擎
    harness = AgentHarness()

    print()
    print("🐣 Agent Harness — 开始考试")
    print(f"   题目总数: {len(tasks)}")
    print(f"   考试范围: Level {', '.join(levels)}")
    print()

    # 逐 Level 考试
    all_results = {}
    for level in levels:
        if level not in LEVEL_FACTORIES:
            print(f"⚠️ Level {level} 没有适配器，跳过")
            continue

        name, factory = LEVEL_FACTORIES[level]
        print(f"📋 Level {level} ({name})...")

        try:
            agent_fn = factory()
            result = harness.run_level(level, tasks, agent_fn)
            all_results[level] = result

            # 打印简要结果
            if result.total:
                print(f"   ✅ {result.passed}/{result.total} 通过 ({result.pass_rate:.0%})")
            else:
                print(f"   ⚠️ 无测试题")

        except Exception as e:
            print(f"   ❌ 测试失败: {e}")

    # 生成报告
    if all_results:
        report = format_report(all_results, verbose=args.verbose)
        print(report)

        if args.export:
            path = export_json(all_results)
            print(f"  📄 JSON 报告已导出: {path}")
    else:
        print("  ⚠️ 没有可运行的测试")


if __name__ == "__main__":
    main()
