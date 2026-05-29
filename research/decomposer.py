"""
深度研究 — Question Decomposer（问题分解器）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

核心思想：
  一个复杂问题 = 多个简单问题的组合。
  先把大问题拆成小问题，逐个击破，最后综合答案。

这是 Research Agent 的第一步——"我需要调查哪些方面？"
"""

from openai import OpenAI


class QuestionDecomposer:
    """
    问题分解器：把一个复杂问题拆成多个可独立调研的子问题。

    例如：
      "Rust 和 Go 哪个更适合写 Web 服务器？"
      → ["Rust Web 框架有哪些？各自特点？",
          "Go Web 框架有哪些？各自特点？",
          "Rust vs Go Web 性能对比数据？",
          "Rust vs Go Web 开发体验对比？"]
    """

    def __init__(self, model: str):
        self.client = OpenAI()
        self.model = model

    def decompose(self, question: str, max_sub_questions: int = 5) -> list[str]:
        """
        把一个问题拆成多个子问题。
        返回子问题列表。
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个问题分解专家。\n"
                        "把一个复杂问题拆成多个可以独立调研的子问题。\n"
                        f"最多拆成 {max_sub_questions} 个。\n"
                        "输出JSON: {\"sub_questions\": [\"子问题1\", \"子问题2\", ...]}\n"
                        "只输出JSON。"
                    )
                },
                {"role": "user", "content": question}
            ],
            response_format={"type": "json_object"},
        )

        import json
        parsed = json.loads(response.choices[0].message.content)
        sub_questions = parsed.get("sub_questions", parsed.get("questions", []))

        # 限制数量
        return sub_questions[:max_sub_questions]
