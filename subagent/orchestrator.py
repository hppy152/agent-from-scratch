"""
SubAgent Orchestrator — 父 Agent 调度子 Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Orchestrator 的核心能力：
  1. 接收用户任务
  2. 决定需要哪些子 Agent
  3. 通过 delegate_task 分发任务
  4. 收集子 Agent 的结果
  5. 综合所有结果给出最终回答

这就是 Hermes 中 Orchestrator + SubAgent 的完整流程。
"""

import json
from dataclasses import dataclass, field
from openai import OpenAI
try:
    from .core import SubAgent, SubAgentResponse
except ImportError:
    from core import SubAgent, SubAgentResponse


@dataclass
class DelegatePlan:
    """任务分发计划"""
    subtasks: list[dict] = field(default_factory=list)
    # 每个 subtask: {"agent": "agent_name", "task": "具体任务描述"}


class SubAgentOrchestrator:
    """
    Orchestrator：能够动态创建和调度子 Agent 的父 Agent。

    和 Level 4 的区别：
      - Level 4: 预定义的固定 Worker（searcher, analyst, writer）
      - Level 6: 动态创建的 SubAgent（根据任务临时决定需要谁）

    这就是从"静态团队"到"动态调度"的进化。
    """

    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI()
        self.registered_agents: dict[str, SubAgent] = {}

    def register_agent(self, agent: SubAgent):
        """注册一个子 Agent（告诉 Orchestrator 有这个人可用）"""
        self.registered_agents[agent.name] = agent

    def delegate_task(self, agent_name: str, task: str) -> SubAgentResponse:
        """
        核心方法：把任务委派给指定的子 Agent。

        这就是 "delegate_task" —— 父 Agent 不亲自干活，
        而是分配给合适的子 Agent，等它完成后再拿结果。
        """
        agent = self.registered_agents.get(agent_name)
        if not agent:
            return SubAgentResponse(
                agent_name=agent_name,
                task=task,
                result=f"错误：子 Agent '{agent_name}' 不存在",
            )

        print(f"    → 委派给 {agent_name}: {task[:50]}...")
        response = agent.run(task)
        print(f"    ← {agent_name} 完成 ({response.steps}步)")

        return response

    def plan(self, user_request: str) -> DelegatePlan:
        """
        让 LLM 规划任务分发：决定需要哪些子 Agent，各自做什么。

        这是 Orchestrator 的"大脑"——它不干活，只做决策。
        """
        agent_list = "\n".join(
            f"  - {name}: {agent.system_prompt[:60]}"
            for name, agent in self.registered_agents.items()
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"你是任务规划者。根据用户请求，决定需要哪些子Agent。\n\n"
                        f"可用的子Agent:\n{agent_list}\n\n"
                        f"输出JSON: {{\"subtasks\": [{{\"agent\": \"Agent名称\", \"task\": \"具体任务描述\"}}]}}\n"
                        f"只输出JSON，不要其他内容。"
                    )
                },
                {"role": "user", "content": user_request}
            ],
            response_format={"type": "json_object"},
        )

        parsed = json.loads(response.choices[0].message.content)
        subtasks = parsed.get("subtasks", [])
        return DelegatePlan(subtasks=subtasks)

    def execute(self, user_request: str) -> str:
        """
        完整流程：规划 → 分发 → 收集 → 综合

        这就是 SubAgent 系统的完整生命周期。
        """
        print(f"\n{'━'*60}")
        print(f"📋 Orchestrator 收到任务: {user_request}")
        print(f"{'━'*60}")

        # 1. 规划
        plan = self.plan(user_request)
        print(f"\n📝 分发计划 ({len(plan.subtasks)} 个子任务):")
        for i, st in enumerate(plan.subtasks, 1):
            print(f"  {i}. {st.get('agent', '?')}: {st.get('task', '?')[:50]}...")

        # 2. 分发并收集
        print(f"\n{'━'*60}")
        print(f"⚡ 执行中...")
        results = []
        for st in plan.subtasks:
            agent_name = st.get("agent", "")
            task_desc = st.get("task", "")
            resp = self.delegate_task(agent_name, task_desc)
            results.append(resp)

        # 3. 综合
        print(f"\n{'━'*60}")
        print(f"📊 综合结果...")
        summary = self._synthesize(user_request, results)
        return summary

    def _synthesize(self, user_request: str, results: list[SubAgentResponse]) -> str:
        """用 LLM 把多个子 Agent 的结果综合成最终回答"""
        parts = []
        for r in results:
            tools_info = ""
            if r.tool_calls:
                tools_info = f"\n  调用了工具: {', '.join(tc['tool'] for tc in r.tool_calls)}"
            parts.append(
                f"### {r.agent_name} 的结果:\n{r.result}{tools_info}"
            )

        combined = "\n\n".join(parts)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是结果综合者。把多个子Agent的结果整合成一个完整、清晰的回答。给出结论和建议。"
                },
                {
                    "role": "user",
                    "content": f"原始请求: {user_request}\n\n各子Agent的结果:\n{combined}"
                }
            ]
        )
        return response.choices[0].message.content
