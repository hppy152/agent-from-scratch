"""
Agent Harness — 测试与评估框架
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

这个包提供了一套完整的 Agent 测试工具：
  - runner: 考试引擎（运行 Agent、收集结果）
  - scorer: 评分器（多种评分策略）
  - report: 报告生成器（终端 + JSON）
  - tasks.json: 题库
"""

from .runner import AgentHarness, Task, TaskResult, HarnessResult
from .scorer import score
from .report import format_report, export_json

__all__ = [
    "AgentHarness", "Task", "TaskResult", "HarnessResult",
    "score", "format_report", "export_json",
]
