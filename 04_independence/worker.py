"""
Level 4 · Worker（专业 Agent）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

每个 Worker 是一个独立的 Agent：
  - 有自己的专长（角色设定）
  - 独立思考和行动
"""

from openai import OpenAI


class Worker:
    """
    专业 Agent。
    就像现实中的专家：你是律师就只处理法律问题，你是会计就只处理财务。
    """

    def __init__(self, name: str, role: str, system_prompt: str = ""):
        self.name = name
        self.role = role
        self.client = OpenAI()
        self.system_prompt = system_prompt or f"你是{role}。专注做好自己的事。"

    def work(self, task: str) -> str:
        """
        执行分配给自己的任务。
        Worker 不关心全局——它只看到自己的任务。
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        return response.choices[0].message.content

    def __repr__(self):
        return f"Worker({self.name}, role={self.role})"


# ═══════════════════════════════════════════
# 预定义的专业 Worker
# ═══════════════════════════════════════════

def create_searcher() -> Worker:
    """搜索专家：擅长信息检索和整理"""
    return Worker(
        name="searcher",
        role="信息搜索与研究专家",
        system_prompt=(
            "你是信息搜索专家。\n"
            "你的任务是调研、搜索、整理信息。\n"
            "给出有条理、有依据的信息汇总。"
        ),
    )


def create_analyst() -> Worker:
    """分析专家：擅长数据分析和对比"""
    return Worker(
        name="analyst",
        role="数据分析与对比专家",
        system_prompt=(
            "你是数据分析专家。\n"
            "你的任务是分析数据、做对比、找规律。\n"
            "给出清晰的分析结论。"
        ),
    )


def create_writer() -> Worker:
    """写作专家：擅长整理和表达"""
    return Worker(
        name="writer",
        role="内容写作与整理专家",
        system_prompt=(
            "你是写作专家。\n"
            "你的任务是把信息整理成清晰、易读的文字。\n"
            "语言简洁有力，结构清晰。"
        ),
    )
