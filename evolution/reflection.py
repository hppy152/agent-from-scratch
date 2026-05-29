"""
自我进化 — Reflection（反思循环）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

核心思想：
  Agent 每次失败后，不是简单地重试，
  而是先"反思"——分析原因、总结教训、形成经验。
  下次遇到类似问题时，参考这些经验，成功率就会提高。

这就是 Reflexion 论文的核心——用自然语言做"自我强化学习"。

传统 ML:  错误 → 梯度下降 → 更新权重
Agent:     错误 → 自然语言反思 → 存入记忆 → 下次参考
"""

import json
import os
from datetime import datetime


class ReflectionMemory:
    """
    反思记忆：存储 Agent 的失败经验和改进建议。

    每条反思包含：
      - 任务：当时在做什么
      - 错误：出了什么问题
      - 反思：分析原因
      - 建议：下次怎么做
    """

    def __init__(self, path: str = "reflections.json"):
        self.path = path
        self.reflections: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.reflections, f, ensure_ascii=False, indent=2)

    def add(self, task: str, error: str, reflection: str, suggestion: str):
        """记录一次反思"""
        entry = {
            "task": task,
            "error": error,
            "reflection": reflection,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat(),
        }
        self.reflections.append(entry)
        self._save()

    def recall(self, task_hint: str = "") -> str:
        """
        回忆相关反思。
        如果给出了 task_hint，只返回和当前任务相关的反思。
        """
        if not self.reflections:
            return "（暂无反思记录）"

        relevant = self.reflections
        if task_hint:
            # 简单关键词匹配
            relevant = [
                r for r in self.reflections
                if any(kw in r["task"] for kw in task_hint.split())
                or any(kw in r.get("reflection", "") for kw in task_hint.split())
            ]
            if not relevant:
                relevant = self.reflections[-3:]  # 取最近 3 条

        lines = []
        for r in relevant[-5:]:  # 最多返回 5 条
            lines.append(
                f"  任务: {r['task']}\n"
                f"  教训: {r['reflection']}\n"
                f"  建议: {r['suggestion']}"
            )
        return "\n\n".join(lines)

    def count(self) -> int:
        return len(self.reflections)

    def recent(self, n: int = 3) -> list[dict]:
        return self.reflections[-n:]


class ReflectionAgent:
    """
    带反思能力的 Agent。

    工作流程：
      1. 收到任务
      2. 回忆相关反思（从经验中学习）
      3. 执行任务
      4. 如果失败 → 自我反思 → 存入记忆
      5. 如果成功 → 提取技能 → 存入技能库
    """

    def __init__(self, llm_call, reflections: ReflectionMemory = None):
        """
        Args:
            llm_call: LLM 调用函数 (messages) -> str
            reflections: 反思记忆存储
        """
        self.llm_call = llm_call
        self.reflections = reflections or ReflectionMemory()

    def think(self, task: str) -> str:
        """
        执行前先思考：回忆相关经验，避免重复犯错。
        """
        # 1. 回忆相关反思
        relevant = self.reflections.recall(task)

        # 2. 构建带经验的 prompt
        prompt = f"你是一个会从经验中学习的Agent。\n\n"
        if relevant and "暂无" not in relevant:
            prompt += f"## 历史经验\n{relevant}\n\n"
            prompt += "请参考以上经验，避免重复犯错。\n\n"
        prompt += f"## 当前任务\n{task}\n\n"
        prompt += "请执行这个任务。"

        return self.llm_call([
            {"role": "user", "content": prompt}
        ])

    def reflect_on_failure(self, task: str, error: str) -> str:
        """
        失败后反思：分析原因，给出改进建议。
        这是自我进化的核心——从错误中学习。
        """
        prompt = (
            f"你刚刚在执行任务时失败了。\n\n"
            f"任务: {task}\n"
            f"错误: {error}\n\n"
            f"请进行自我反思：\n"
            f"1. 分析失败原因\n"
            f"2. 总结教训\n"
            f"3. 给出具体的改进建议\n"
            f"用中文回答，简洁明了。"
        )

        reflection = self.llm_call([
            {"role": "user", "content": prompt}
        ])

        # 存入反思记忆
        self.reflections.add(
            task=task,
            error=error,
            reflection=reflection,
            suggestion=reflection,  # 反思本身就是建议
        )

        return reflection

    def execute_with_reflection(self, task: str) -> dict:
        """
        完整流程：思考 → 执行 → 失败则反思 → 返回结果
        """
        # 1. 带经验思考
        result = self.think(task)

        # 2. 检查是否成功（简单判断：输出中是否包含"错误"或"失败"）
        if any(kw in result.lower() for kw in ["错误", "失败", "error", "抱歉", "无法"]):
            # 3. 失败 → 反思
            reflection = self.reflect_on_failure(task, result)
            return {
                "success": False,
                "output": result,
                "reflection": reflection,
            }

        return {
            "success": True,
            "output": result,
            "reflection": None,
        }
