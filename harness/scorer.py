"""
Agent Harness — 评分器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

多种评分策略，根据题目类型选择不同的打分方式。

策略:
  exact     — 精确匹配（输出必须完全等于期望值）
  contains  — 包含匹配（输出中包含期望值即可）
  tool      — 工具验证（Agent 必须调用了指定工具）
  tool_args — 工具参数验证（调用工具时参数正确）
  keyword   — 关键词匹配（输出中包含多个关键词）
  llm       — LLM 评分（用另一个 LLM 判断质量）
"""

import re


def score(task, output: str, tool_calls: list[dict]) -> tuple[float, bool, dict]:
    """
    对一道题打分。

    返回: (score, passed, details)
        score: 0.0 ~ 1.0
        passed: 是否通过
        details: 评分细节
    """
    strategy = task.scorer

    if strategy == "exact":
        return _score_exact(task.expected, output)
    elif strategy == "contains":
        return _score_contains(task.expected, output)
    elif strategy == "tool":
        return _score_tool(task.expected_tool, tool_calls)
    elif strategy == "tool_args":
        return _score_tool_args(task.expected_tool, task.expected, tool_calls)
    elif strategy == "keyword":
        return _score_keyword(task.expected, output)
    elif strategy == "any":
        # 只要有输出就算通过（用于冒烟测试）
        return _score_any(output)
    else:
        # 默认包含匹配
        return _score_contains(task.expected, output)


def _score_exact(expected: str, output: str) -> tuple[float, bool, dict]:
    """精确匹配：输出必须完全等于期望值"""
    passed = output.strip() == expected.strip()
    return (1.0 if passed else 0.0, passed, {"expected": expected, "actual": output[:200]})


def _score_contains(expected: str, output: str) -> tuple[float, bool, dict]:
    """包含匹配：输出中包含期望值"""
    if not expected:
        # 没有期望值，只要有输出就算通过
        return _score_any(output)
    passed = expected.lower() in output.lower()
    return (1.0 if passed else 0.0, passed, {"expected": expected, "found": passed})


def _score_tool(expected_tool: str, tool_calls: list[dict]) -> tuple[float, bool, dict]:
    """工具验证：Agent 必须调用了指定工具"""
    if not expected_tool:
        return (1.0, True, {"note": "无工具要求"})
    called_tools = [tc.get("tool", tc.get("name", "")) for tc in tool_calls]
    passed = expected_tool in called_tools
    return (1.0 if passed else 0.0, passed, {"expected_tool": expected_tool, "actual_tools": called_tools})


def _score_tool_args(expected_tool: str, expected_args: str, tool_calls: list[dict]) -> tuple[float, bool, dict]:
    """工具参数验证：调用指定工具时参数包含期望值"""
    for tc in tool_calls:
        tool_name = tc.get("tool", tc.get("name", ""))
        if tool_name == expected_tool:
            args_str = json.dumps(tc.get("args", tc.get("arguments", {})))
            if expected_args.lower() in args_str.lower():
                return (1.0, True, {"tool": expected_tool, "args_match": True})
    return (0.0, False, {"expected_tool": expected_tool, "expected_args": expected_args})


def _score_keyword(expected: str, output: str) -> tuple[float, bool, dict]:
    """关键词匹配：期望值用逗号分隔多个关键词，匹配越多分越高"""
    if not expected:
        return _score_any(output)
    keywords = [k.strip().lower() for k in expected.split(",")]
    matches = sum(1 for kw in keywords if kw in output.lower())
    score = matches / len(keywords) if keywords else 0
    return (score, score >= 0.5, {"keywords": keywords, "matched": matches, "total": len(keywords)})


def _score_any(output: str) -> tuple[float, bool, dict]:
    """冒烟测试：只要有输出就算通过"""
    passed = bool(output and output.strip())
    return (1.0 if passed else 0.0, passed, {"has_output": passed})


# 需要 import（tool_args 策略用了）
import json
