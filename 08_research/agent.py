"""
Level 8 · 我会研究了
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

深度研究 Agent：
  1. 分解问题（Decomposer）
  2. 逐个调研（Investigator）
  3. 综合报告（Synthesizer）

运行: python 08_research/agent.py（从项目根目录）
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODEL
from tools import TOOL_SCHEMAS, execute_tool
from research.decomposer import QuestionDecomposer
from research.investigator import Investigator
from research.synthesizer import Synthesizer

from openai import OpenAI


class DeepResearchAgent:
    """深度研究 Agent"""

    def __init__(self):
        self.decomposer = QuestionDecomposer(MODEL)
        self.investigator = Investigator(MODEL, TOOL_SCHEMAS, execute_tool)
        self.synthesizer = Synthesizer(MODEL)

    def research(self, question: str, max_sub: int = 4) -> str:
        """
        完整研究流程：分解 → 调研 → 综合
        """
        print(f"\n🔬 开始深度研究...")

        # 1. 分解
        print(f"\n📋 分解问题...")
        sub_questions = self.decomposer.decompose(question, max_sub)
        print(f"   拆出 {len(sub_questions)} 个子问题:")
        for i, sq in enumerate(sub_questions, 1):
            print(f"   {i}. {sq}")

        # 2. 逐个调研
        print(f"\n🔍 调研中...")
        investigations = []
        for i, sq in enumerate(sub_questions, 1):
            print(f"   → 子问题 {i} 调研中...", end=" ", flush=True)
            result = self.investigator.investigate(sq, max_steps=3)
            investigations.append(result)
            print("✅")

        # 3. 综合
        print(f"\n📊 综合报告...")
        report = self.synthesizer.synthesize(question, investigations)

        return report


def main():
    agent = DeepResearchAgent()

    print("=" * 60)
    print("  🔬 Agent v8.0 — 深度研究版")
    print("  输入 'exit' 退出。")
    print("=" * 60)

    while True:
        user_input = input("\n你: ")

        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nAgent: 再见，造物者。研究永无止境。")
            break

        report = agent.research(user_input)
        print(f"\n{'━'*60}")
        print(f"📝 研究报告:\n\n{report}")
        print(f"{'━'*60}")


if __name__ == "__main__":
    main()
