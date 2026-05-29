"""
Agent Harness — 考试引擎
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Harness 的核心：把 Agent 当黑盒，喂题、观察、打分。

这个模块是独立的——它可以测试任何 Level 的 Agent，
也可以测试你自己写的 Agent。只要你的 Agent 能接收字符串输入、
返回字符串输出，就能被 harness 测试。

这就是大厂评测 Agent 的基本思路。
"""

import json
import time
import traceback
from dataclasses import dataclass, field
from typing import Callable


# ═══════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════

@dataclass
class Task:
    """
    一道考题。

    字段:
        id: 唯一标识
        input: 给 Agent 的输入
        expected: 期望输出（用于精确匹配/包含匹配）
        expected_tool: 期望 Agent 调用的工具名（用于工具验证）
        scorer: 用哪种评分策略（默认 "contains"）
        description: 题目描述（给人看的）
        level: 属于哪个 Level（用于分组）
    """
    id: str
    input: str
    expected: str = ""
    expected_tool: str = ""
    scorer: str = "contains"
    description: str = ""
    level: str = "0"


@dataclass
class TaskResult:
    """一道题的结果"""
    task: Task
    output: str
    tool_calls: list[dict]
    score: float        # 0.0 ~ 1.0
    passed: bool
    latency_ms: float
    steps: int          # Agent 推理了几步
    error: str = ""


@dataclass
class HarnessResult:
    """整场考试的结果"""
    level: str
    results: list[TaskResult]
    total: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0
    avg_score: float = 0.0
    avg_latency_ms: float = 0.0
    total_tool_calls: int = 0
    total_steps: int = 0


# ═══════════════════════════════════════════
# Harness 核心
# ═══════════════════════════════════════════

class AgentHarness:
    """
    考试引擎：运行 Agent、收集结果、打分。

    使用方式:
        harness = AgentHarness(agent_fn=my_agent)
        result = harness.run_level("1", tasks)
        print(result)
    """

    def __init__(self, agent_fn: Callable = None):
        """
        Args:
            agent_fn: Agent 函数，签名 (input: str) -> AgentResponse
                      AgentResponse 需要有 .output (str) 和 .tool_calls (list)
        """
        self.agent_fn = agent_fn

    def run_task(self, task: Task, agent_fn: Callable = None) -> TaskResult:
        """
        跑一道题。

        返回 TaskResult，包含输出、得分、耗时、工具调用等。
        """
        fn = agent_fn or self.agent_fn
        if not fn:
            raise ValueError("未设置 agent_fn")

        start = time.time()
        try:
            response = fn(task.input)
            latency = (time.time() - start) * 1000

            output = getattr(response, "output", str(response))
            tool_calls = getattr(response, "tool_calls", []) or []
            steps = getattr(response, "steps", 1)

            # 评分
            from .scorer import score
            s, passed, details = score(task, output, tool_calls)

            return TaskResult(
                task=task,
                output=output,
                tool_calls=tool_calls,
                score=s,
                passed=passed,
                latency_ms=latency,
                steps=steps,
            )

        except Exception as e:
            latency = (time.time() - start) * 1000
            return TaskResult(
                task=task,
                output="",
                tool_calls=[],
                score=0.0,
                passed=False,
                latency_ms=latency,
                steps=0,
                error=traceback.format_exc(),
            )

    def run_level(self, level: str, tasks: list[Task], agent_fn: Callable = None) -> HarnessResult:
        """跑一个 Level 的全部题目"""
        level_tasks = [t for t in tasks if t.level == level]
        if not level_tasks:
            return HarnessResult(level=level, results=[], total=0)

        results = [self.run_task(t, agent_fn) for t in level_tasks]

        total = len(results)
        passed = sum(1 for r in results if r.passed)

        return HarnessResult(
            level=level,
            results=results,
            total=total,
            passed=passed,
            failed=total - passed,
            pass_rate=passed / total if total else 0,
            avg_score=sum(r.score for r in results) / total if total else 0,
            avg_latency_ms=sum(r.latency_ms for r in results) / total if total else 0,
            total_tool_calls=sum(len(r.tool_calls) for r in results),
            total_steps=sum(r.steps for r in results),
        )

    def run_all(self, tasks: list[Task], agent_fn: Callable = None) -> dict[str, HarnessResult]:
        """跑全部 Level，返回 {level: HarnessResult}"""
        levels = sorted(set(t.level for t in tasks))
        return {level: self.run_level(level, tasks, agent_fn) for level in levels}
