"""
Skill Loader — 知识加载器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Skill 是什么？
  - 一份 Markdown 文档，描述"遇到某类任务时怎么做"
  - 有 YAML frontmatter（元数据）和 Markdown body（知识内容）
  - Agent 在回答前先匹配相关 Skill，把知识注入 prompt

这就是 Hermes/OpenClaw 中 Skill 系统的最小实现。
"""

import os
import re


class Skill:
    """一个技能单元"""

    def __init__(self, name: str, description: str, tags: list[str], content: str):
        self.name = name
        self.description = description
        self.tags = tags
        self.content = content

    def __repr__(self):
        return f"Skill({self.name}, tags={self.tags})"


class SkillLoader:
    """
    扫描 skills/ 目录，根据用户输入匹配并加载相关 Skill。

    目录结构：
      skills/
        web-search/
          SKILL.md      ← 必须叫这个名字
        code-review/
          SKILL.md
    """

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
        self.skills: dict[str, Skill] = {}
        self._scan()

    def _scan(self):
        """扫描所有 skills，解析 SKILL.md 的 frontmatter"""
        if not os.path.exists(self.skills_dir):
            print(f"  ⚠️ skills 目录不存在: {self.skills_dir}")
            return

        for name in sorted(os.listdir(self.skills_dir)):
            skill_file = os.path.join(self.skills_dir, name, "SKILL.md")
            if not os.path.isfile(skill_file):
                continue

            with open(skill_file, "r", encoding="utf-8") as f:
                raw = f.read()

            # 解析 YAML frontmatter（用正则，不依赖 pyyaml）
            description = ""
            tags = []
            body = raw

            if raw.startswith("---"):
                parts = raw.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1].strip()
                    body = parts[2].strip()

                    # 简易 YAML 解析
                    for line in frontmatter.split("\n"):
                        line = line.strip()
                        if line.startswith("description:"):
                            description = line.split(":", 1)[1].strip().strip("'\"")
                        elif line.startswith("tags:"):
                            # 处理 [tag1, tag2] 格式
                            tag_str = line.split(":", 1)[1].strip()
                            if tag_str.startswith("["):
                                tags = [t.strip().strip("'\"") for t in tag_str[1:-1].split(",")]
                            else:
                                tags = [tag_str.strip("'\"")]

            self.skills[name] = Skill(
                name=name,
                description=description,
                tags=tags,
                content=body,
            )

    def match(self, user_input: str, top_k: int = 2) -> list[str]:
        """
        根据用户输入，返回最匹配的 skill 名称。
        匹配逻辑：
          - tags 关键词出现在用户输入中（精确匹配 + 子串匹配）
          - description 关键词匹配
          - skill 名称匹配
        """
        scores = {}
        user_lower = user_input.lower()
        user_words = set(user_lower.split())

        for name, skill in self.skills.items():
            score = 0
            # tags 匹配（精确 + 子串 + 前缀）
            for tag in skill.tags:
                tag_lower = tag.lower()
                if tag_lower in user_lower:
                    score += 3  # 精确子串匹配（"搜索" 在 "搜索xxx" 中）
                elif len(tag_lower) >= 2 and tag_lower[:1] in user_lower:
                    score += 2  # 首字匹配（"搜" 匹配 "搜索"）
                elif any(c in user_lower for c in tag_lower if len(c) >= 1):
                    score += 1  # 任意字符匹配

            # description 关键词匹配
            desc_words = set(skill.description.lower().split())
            score += len(user_words & desc_words)

            # skill 名称匹配（如 "web" 匹配 "web-search"）
            name_parts = name.replace("-", " ").split()
            if any(part in user_lower for part in name_parts):
                score += 2

            if score > 0:
                scores[name] = score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [name for name, _ in ranked[:top_k]]

    def load(self, skill_names: list[str]) -> str:
        """加载指定 skills 的内容，返回可注入 prompt 的文本"""
        parts = []
        for name in skill_names:
            skill = self.skills.get(name)
            if skill:
                parts.append(
                    f"### 技能: {skill.name}\n"
                    f"*{skill.description}*\n\n"
                    f"{skill.content}"
                )
        return "\n\n---\n\n".join(parts)

    def list_all(self) -> str:
        """列出所有可用技能"""
        if not self.skills:
            return "（没有加载任何技能）"
        lines = []
        for name, skill in self.skills.items():
            tags = ", ".join(skill.tags) if skill.tags else "无标签"
            lines.append(f"  • {name}: {skill.description} [{tags}]")
        return "\n".join(lines)
