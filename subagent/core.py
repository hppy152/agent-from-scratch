"""
SubAgent — 子 Agent 核心
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

子 Agent 的本质：
  - 一个独立的 LLM 会话（有自己的消息历史）
  - 专注于一个特定任务
  - 完成后把结果返回给父 Agent

这就是 Hermes 中 SubAgent 的最小实现。
"""

import json
from dataclasses import dataclass, field
from openai import OpenAI


@dataclass
class SubAgentResponse:
    """子 Agent 的返回结果"""
    agent_name: str       # 子 Agent 名称
    task: str             # 分配的任务
    result: str           # 执行结果
    tool_calls: list = field(default_factory=list)  # 工具调用记录
    steps: int = 0        # 推理步数


class SubAgent:
    """
    子 Agent：一个独立的 LLM 会话。

    关键特性：
      - 隔离的上下文（不共享父 Agent 的对话历史）
      - 专注的职责（只处理分配给它的任务）
      - 独立的工具集（可以有和父 Agent 不同的工具）
    """

    def __init__(
        self,
        name: str,
        model: str,
        system_prompt: str = "",
        tools: list[dict] = None,
        tool_executor: callable = None,
        max_steps: int = 5,
    ):
        """
        Args:
            name: 子 Agent 的名字（如 "搜索员"）
            model: LLM 模型名
            system_prompt: 系统提示（定义角色和能力）
            tools: 工具定义列表（OpenAI 格式）
            tool_executor: 工具执行函数 (name, args) -> result_str
            max_steps: 最大推理步数
        """
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.client = OpenAI()

    def run(self, task: str) -> SubAgentResponse:
        """
        执行一个任务。

        这是一个完整的 ReAct 循环——
        子 Agent 独立思考、调用工具、直到完成任务。
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        all_tool_calls = []
        steps = 0

        for step in range(self.max_steps):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto",
            )
            msg = response.choices[0].message
            steps += 1

            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)

                    if self.tool_executor:
                        result = self.tool_executor(name, args)
                    else:
                        result = f"工具 {name} 未配置执行器"

                    all_tool_calls.append({
                        "tool": name,
                        "args": args,
                        "result": result[:200],
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
            else:
                # 任务完成
                return SubAgentResponse(
                    agent_name=self.name,
                    task=task,
                    result=msg.content,
                    tool_calls=all_tool_calls,
                    steps=steps,
                )

        # 达到最大步数
        return SubAgentResponse(
            agent_name=self.name,
            task=task,
            result="任务未完成（达到最大步数）",
            tool_calls=all_tool_calls,
            steps=steps,
        )

    def __repr__(self):
        return f"SubAgent({self.name}, tools={len(self.tools)})"
