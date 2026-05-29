"""
自我进化 — Skill Library（技能库）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

核心思想：
  Agent 每次成功完成任务后，自动提取"可复用的技能"，
  存入技能库。下次遇到类似任务时，直接复用，不用从零开始。

这就是 Voyager 论文的核心——终身学习的 Agent 不断积累技能。

Voyager 在 Minecraft 中：
  成功砍树 → 提取技能"砍树.js" → 存入技能库
  下次需要木头 → 检索"砍树.js" → 直接复用

我们简化为：
  成功完成任务 → 提取 Skill 描述 → 存入 JSON 文件
  下次类似任务 → 检索匹配 → 注入 prompt
"""

import json
import os
from datetime import datetime


class Skill:
    """一个可复用的技能"""

    def __init__(self, name: str, description: str, steps: list[str],
                 trigger: str = "", examples: list[str] = None):
        """
        Args:
            name: 技能名称
            description: 技能描述
            steps: 执行步骤
            trigger: 触发条件（什么情况下用这个技能）
            examples: 使用示例
        """
        self.name = name
        self.description = description
        self.steps = steps
        self.trigger = trigger
        self.examples = examples or []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "trigger": self.trigger,
            "examples": self.examples,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Skill":
        return cls(**data)

    def to_prompt(self) -> str:
        """转为可注入 prompt 的文本"""
        steps_text = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(self.steps))
        return (
            f"### 技能: {self.name}\n"
            f"触发条件: {self.trigger}\n"
            f"描述: {self.description}\n"
            f"步骤:\n{steps_text}"
        )

    def __repr__(self):
        return f"Skill({self.name}, steps={len(self.steps)})"


class SkillLibrary:
    """
    技能库：存储和检索可复用的技能。

    Agent 成功完成任务后，自动调用 extract_skill 提取技能，
    然后用 store 保存。下次遇到类似任务，用 retrieve 检索。
    """

    def __init__(self, path: str = "skill_library.json"):
        self.path = path
        self.skills: list[Skill] = self._load()

    def _load(self) -> list[Skill]:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Skill.from_dict(s) for s in data]
        return []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.skills], f, ensure_ascii=False, indent=2)

    def store(self, skill: Skill):
        """存储一个新技能"""
        # 检查是否已存在同名技能
        existing = [s for s in self.skills if s.name == skill.name]
        if existing:
            # 更新已有技能
            idx = self.skills.index(existing[0])
            self.skills[idx] = skill
        else:
            self.skills.append(skill)
        self._save()

    def retrieve(self, query: str, top_k: int = 3) -> list[Skill]:
        """
        根据查询检索相关技能。
        匹配 trigger、name、description 中的关键词。
        """
        scores = []
        query_lower = query.lower()

        for skill in self.skills:
            score = 0
            # trigger 匹配
            if skill.trigger and any(kw in query_lower for kw in skill.trigger.lower().split()):
                score += 3
            # name 匹配
            if any(part in query_lower for part in skill.name.lower().split()):
                score += 2
            # description 匹配
            if any(kw in query_lower for kw in skill.description.lower().split()):
                score += 1

            if score > 0:
                scores.append((score, skill))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [skill for _, skill in scores[:top_k]]

    def to_context(self, query: str) -> str:
        """检索相关技能并转为 prompt 上下文"""
        skills = self.retrieve(query)
        if not skills:
            return ""
        parts = [s.to_prompt() for s in skills]
        return "\n\n".join(parts)

    def count(self) -> int:
        return len(self.skills)

    def list_all(self) -> str:
        """列出所有技能"""
        if not self.skills:
            return "（技能库为空）"
        lines = []
        for s in self.skills:
            lines.append(f"  • {s.name}: {s.description} (步骤: {len(s.steps)})")
        return "\n".join(lines)
