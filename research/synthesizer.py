"""
深度研究 — Synthesizer（综合器）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

核心思想：
  把多个子问题的调研结果综合成一个完整的、有结构的研究报告。

这是 Research Agent 的最后一步——"综合所有发现，给出最终答案。"
"""

from openai import OpenAI


class Synthesizer:
    """
    综合器：把多个调研结果整合成最终报告。
    """

    def __init__(self, model: str):
        self.client = OpenAI()
        self.model = model

    def synthesize(self, original_question: str, investigations: list[dict]) -> str:
        """
        综合所有调研结果，生成最终报告。

        Args:
            original_question: 原始问题
            investigations: 各子问题的调研结果列表
        """
        # 构建调研摘要
        parts = []
        for i, inv in enumerate(investigations, 1):
            parts.append(
                f"### 子问题 {i}: {inv['question']}\n"
                f"{inv['findings']}"
            )

        all_findings = "\n\n".join(parts)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个研究综合专家。\n"
                        "把多个子问题的调研结果整合成一份完整的研究报告。\n\n"
                        "报告格式：\n"
                        "1. 概述（简要回答原始问题）\n"
                        "2. 详细分析（按子问题分节）\n"
                        "3. 结论与建议\n\n"
                        "要求：客观、有条理、有深度。"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"## 原始问题\n{original_question}\n\n"
                        f"## 各子问题的调研结果\n\n{all_findings}"
                    )
                }
            ],
            max_tokens=1500,
        )

        return response.choices[0].message.content


class DeepResearchAgent:
    """
    深度研究 Agent：完整的多步研究流程。

    流程：
      1. 分解问题（Decomposer）
      2. 并行调研（Investigator × N）
      3. 综合报告（Synthesizer）

    这就是 GPT Researcher、STORM 等项目的核心思路。
    """

    def __init__(self, model: str, tools: list[dict] = None, tool_executor: callable = None):
        from .decomposer import QuestionDecomposer
        self.decomposer = QuestionDecomposer(model)
        self.investigator = Investigator(model, tools, tool_executor)
        self.synthesizer = Synthesizer(model)

    def research(self, question: str, max_sub_questions: int = 4) -> dict:
        """
        执行完整的研究流程。

        返回:
            {
                "question": 原始问题,
                "sub_questions": 分解出的子问题,
                "investigations": 各子问题的调研结果,
                "report": 最终研究报告,
            }
        """
        # 1. 分解问题
        sub_questions = self.decomposer.decompose(question, max_sub_questions)

        # 2. 逐个调研（实际项目中可以并行）
        investigations = []
        for sq in sub_questions:
            result = self.investigator.investigate(sq)
            investigations.append(result)

        # 3. 综合报告
        report = self.synthesizer.synthesize(question, investigations)

        return {
            "question": question,
            "sub_questions": sub_questions,
            "investigations": investigations,
            "report": report,
        }
