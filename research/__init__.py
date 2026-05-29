"""
深度研究系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  - Decomposer: 问题分解器
  - Investigator: 调研员
  - Synthesizer: 综合器
  - DeepResearchAgent: 完整研究流程
"""

from .decomposer import QuestionDecomposer
from .investigator import Investigator
from .synthesizer import Synthesizer, DeepResearchAgent

__all__ = [
    "QuestionDecomposer", "Investigator",
    "Synthesizer", "DeepResearchAgent",
]
