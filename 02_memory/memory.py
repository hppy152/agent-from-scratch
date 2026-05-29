"""
Level 2 · 记忆系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

三层记忆：
  1. 短期记忆 — 对话消息列表（内存中）
  2. 摘要压缩 — 对话太长时压缩旧消息
  3. 长期记忆 — 跨对话持久化到文件
"""

import json
import os
from datetime import datetime


# ═══════════════════════════════════════════
# 短期记忆：对话缓冲区
# ═══════════════════════════════════════════

class ConversationBuffer:
    """
    管理当前对话的消息列表。
    当消息太多时，自动压缩最旧的消息为摘要。
    """

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: list[dict] = []

    def add(self, message: dict):
        """添加一条消息"""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self._compress()

    def get_messages(self) -> list[dict]:
        """获取当前所有消息"""
        return self.messages.copy()

    def _compress(self):
        """
        压缩策略：保留 system prompt + 最近一半的消息，
        中间的旧消息压缩为摘要。
        """
        system_msg = self.messages[0]
        mid = len(self.messages) // 2
        old_messages = self.messages[1:mid]
        new_messages = self.messages[mid:]

        summary_parts = []
        for msg in old_messages:
            role = "用户" if msg["role"] == "user" else "Agent"
            content = msg.get("content", "")
            if content:
                summary_parts.append(f"{role}: {content[:100]}")

        summary = "；".join(summary_parts)

        self.messages = [
            system_msg,
            {
                "role": "system",
                "content": f"[对话摘要] 之前的对话内容：{summary}"
            },
            *new_messages,
        ]


# ═══════════════════════════════════════════
# 长期记忆：跨对话持久化
# ═══════════════════════════════════════════

class LongTermMemory:
    """
    重要的事实保存到文件，下次启动时自动加载。
    就像人的长期记忆——写在纸上，不会忘记。
    """

    def __init__(self, path: str = "long_term_memory.json"):
        self.path = path
        self.facts: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.facts, f, ensure_ascii=False, indent=2)

    def remember(self, fact: str, category: str = "general"):
        """记住一个新事实"""
        entry = {
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }
        self.facts.append(entry)
        self._save()

    def recall(self, category: str = None) -> str:
        """回忆记忆"""
        if category:
            filtered = [f for f in self.facts if f["category"] == category]
        else:
            filtered = self.facts

        if not filtered:
            return "（我还没有任何记忆）"

        lines = []
        for f in filtered:
            lines.append(f"  [{f['category']}] {f['fact']}")
        return "\n".join(lines)

    def search(self, keyword: str) -> str:
        """搜索记忆"""
        results = [f for f in self.facts if keyword in f["fact"]]
        if not results:
            return f"没有找到包含 '{keyword}' 的记忆"
        return "\n".join(f"  [{f['category']}] {f['fact']}" for f in results)

    def count(self) -> int:
        return len(self.facts)


# ═══════════════════════════════════════════
# 记忆提取器
# ═══════════════════════════════════════════

def extract_facts_from_message(message: str) -> list[str]:
    """
    从用户消息中提取值得记住的事实。
    规则：包含"记住"、"我叫"、"我喜欢"等关键词时提取。
    """
    keywords = ["记住", "我叫", "我是", "我喜欢", "我不喜欢", "我的", "别忘了"]
    facts = []
    for kw in keywords:
        if kw in message:
            facts.append(message)
            break
    return facts
