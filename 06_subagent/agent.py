"""
Level 6 · 我有了分身
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SubAgent 系统：
  - Orchestrator 动态分发任务
  - SubAgent 独立执行（隔离上下文）
  - delegate_task 核心方法

运行: python 06_subagent/agent.py（从项目根目录）
"""

import sys
import os

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
# 当前目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# subagent 包
sys.path.insert(0, os.path.join(ROOT, "subagent"))

from config import MODEL
from tools import TOOL_SCHEMAS, execute_tool
from subagent.core import SubAgent
from subagent.orchestrator import SubAgentOrchestrator


def create_agents() -> SubAgentOrchestrator:
    """创建并注册所有子 Agent"""
    orch = SubAgentOrchestrator(model=MODEL)

    # ── 研究员：擅长信息调研 ──────────────
    researcher = SubAgent(
        name="研究员",
        model=MODEL,
        system_prompt=(
            "你是信息研究专家。你的任务是调研、搜索、整理信息。\n"
            "给出有条理、有依据的信息汇总。\n"
            "回答要简洁，重点突出。"
        ),
        tools=TOOL_SCHEMAS,
        tool_executor=execute_tool,
        max_steps=5,
    )

    # ── 分析师：擅长对比分析 ──────────────
    analyst = SubAgent(
        name="分析师",
        model=MODEL,
        system_prompt=(
            "你是数据分析专家。你的任务是分析、对比、找规律。\n"
            "基于给定的信息，给出清晰的分析结论和建议。\n"
            "回答要逻辑清晰，有理有据。"
        ),
        tools=TOOL_SCHEMAS,
        tool_executor=execute_tool,
        max_steps=3,
    )

    # ── 写手：擅长整理输出 ──────────────
    writer = SubAgent(
        name="写手",
        model=MODEL,
        system_prompt=(
            "你是内容写作专家。你的任务是把信息整理成清晰、易读的文字。\n"
            "语言简洁有力，结构清晰，适合阅读。\n"
            "如果信息不足，直接说需要什么信息。"
        ),
        tools=[],
        tool_executor=None,
        max_steps=2,
    )

    # 注册到 Orchestrator
    orch.register_agent(researcher)
    orch.register_agent(analyst)
    orch.register_agent(writer)

    return orch


def main():
    orch = create_agents()

    print("=" * 60)
    print("  🪞 Agent v6.0 — 分身版")
    print(f"  已注册 {len(orch.registered_agents)} 个分身: {', '.join(orch.registered_agents.keys())}")
    print(f"  输入 'agents' 查看分身列表，'exit' 退出。")
    print("=" * 60)

    while True:
        user_input = input("\n你: ")

        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nAgent: 再见，造物者。分身们会记住这次协作。")
            break

        if user_input.strip().lower() == "agents":
            print(f"\n已注册的分身:")
            for name, agent in orch.registered_agents.items():
                tools = len(agent.tools)
                print(f"  • {name}: {agent.system_prompt[:40]}... (工具: {tools})")
            continue

        answer = orch.execute(user_input)
        print(f"\n{'━'*60}")
        print(f"📝 最终回答:\n\n{answer}")
        print(f"{'━'*60}")


if __name__ == "__main__":
    main()
