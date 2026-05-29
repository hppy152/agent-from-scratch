"""
深度研究 — Investigator（调研员）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

核心思想：
  对每个子问题进行独立调研——搜索信息、整理分析、给出结论。

这是 Research Agent 的第二步——"这个子问题的答案是什么？"
"""

import json
from openai import OpenAI


class Investigator:
    """
    调研员：对一个子问题进行深入调研。

    工作方式：
      1. 分析子问题，确定搜索方向
      2. 调用搜索工具获取信息
      3. 整理分析，给出结论
    """

    def __init__(self, model: str, tools: list[dict] = None, tool_executor: callable = None):
        self.client = OpenAI()
        self.model = model
        self.tools = tools or []
        self.tool_executor = tool_executor

    def investigate(self, sub_question: str, max_steps: int = 3) -> dict:
        """
        调研一个子问题。

        返回:
            {
                "question": 子问题,
                "findings": 调研发现,
                "sources": 信息来源,
                "conclusion": 结论,
                "tool_calls": 工具调用记录
            }
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个深入的研究调研员。\n"
                    "你的任务是对一个问题进行调研，给出有依据的结论。\n"
                    "如果需要搜索信息，使用搜索工具。\n"
                    "回答要客观、有条理、引用来源。"
                )
            },
            {"role": "user", "content": f"请调研以下问题：{sub_question}"}
        ]

        tool_calls = []
        findings = ""

        for step in range(max_steps):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if msg.tool_calls and self.tool_executor:
                messages.append(msg)
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    result = self.tool_executor(name, args)
                    tool_calls.append({"tool": name, "args": args, "result": result[:200]})
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
                findings = msg.content or ""
            else:
                findings = msg.content
                break

        return {
            "question": sub_question,
            "findings": findings,
            "tool_calls": tool_calls,
        }
