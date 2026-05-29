"""
Agent Harness — 报告生成器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

把考试结果转换成人类可读的报告。
支持终端彩色输出和 JSON 导出。
"""

import json
from datetime import datetime


def format_report(results: dict, verbose: bool = False) -> str:
    """
    生成完整的考试报告。

    Args:
        results: {level: HarnessResult} 字典
        verbose: 是否显示每道题的详情
    """
    lines = []

    # ── 标题 ──────────────────────────────
    lines.append("")
    lines.append("╔══════════════════════════════════════════════════════╗")
    lines.append("║         🐣 Agent From Scratch — 考试报告             ║")
    lines.append(f"║         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                          ║")
    lines.append("╚══════════════════════════════════════════════════════╝")
    lines.append("")

    # ── 总览 ──────────────────────────────
    all_results = []
    for level in sorted(results.keys()):
        r = results[level]
        all_results.extend(r.results)

    total_all = len(all_results)
    passed_all = sum(1 for r in all_results if r.passed)
    rate_all = passed_all / total_all if total_all else 0

    lines.append(f"  总计: {total_all} 题 | 通过: {passed_all} | 失败: {total_all - passed_all} | 通过率: {rate_all:.0%}")
    lines.append("")

    # ── 各 Level 详情 ──────────────────────
    lines.append("  ┌─────────┬──────┬──────┬────────┬──────────┬──────────┐")
    lines.append("  │ Level   │ 总题 │ 通过 │ 通过率 │ 平均耗时 │ 工具调用 │")
    lines.append("  ├─────────┼──────┼──────┼────────┼──────────┼──────────┤")

    for level in sorted(results.keys()):
        r = results[level]
        rate = f"{r.pass_rate:.0%}" if r.total else "N/A"
        latency = f"{r.avg_latency_ms:.0f}ms" if r.total else "N/A"
        tools = str(r.total_tool_calls) if r.total else "0"
        lines.append(
            f"  │ Level {level} │  {r.total:>2}  │  {r.passed:>2}  │  {rate:>4}  │  {latency:>6}  │    {tools:>4}  │"
        )

    lines.append("  └─────────┴──────┴──────┴────────┴──────────┴──────────┘")
    lines.append("")

    # ── 各 Level 详细结果 ──────────────────
    for level in sorted(results.keys()):
        r = results[level]
        if not r.results:
            continue

        lines.append(f"  ━━━ Level {level} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for tr in r.results:
            status = "✅" if tr.passed else "❌"
            lines.append(f"  {status} [{tr.task.id}] {tr.task.description}")
            lines.append(f"     输入: {tr.task.input}")
            if tr.output:
                lines.append(f"     输出: {tr.output[:100]}{'...' if len(tr.output) > 100 else ''}")
            if tr.tool_calls:
                tools_str = ", ".join(
                    f"{tc.get('tool', tc.get('name', '?'))}({tc.get('args', tc.get('arguments', {}))})"
                    for tc in tr.tool_calls
                )
                lines.append(f"     工具: {tools_str}")
            lines.append(f"     得分: {tr.score:.2f} | 耗时: {tr.latency_ms:.0f}ms | 步骤: {tr.steps}")
            if tr.error:
                lines.append(f"     错误: {tr.error[:80]}...")
            lines.append("")

    # ── 总结 ──────────────────────────────
    lines.append("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if rate_all >= 0.9:
        lines.append("  🏆 优秀！你的 Agent 表现非常好。")
    elif rate_all >= 0.7:
        lines.append("  👍 不错！大部分题目都通过了。")
    elif rate_all >= 0.5:
        lines.append("  💪 还行，有些地方需要改进。")
    else:
        lines.append("  🔧 需要加油，检查一下失败的题目。")

    lines.append("")

    return "\n".join(lines)


def export_json(results: dict, path: str = "harness_results.json"):
    """导出结果为 JSON 文件"""
    data = {}
    for level, r in results.items():
        data[level] = {
            "total": r.total,
            "passed": r.passed,
            "failed": r.failed,
            "pass_rate": r.pass_rate,
            "avg_score": r.avg_score,
            "avg_latency_ms": r.avg_latency_ms,
            "total_tool_calls": r.total_tool_calls,
            "results": [
                {
                    "id": tr.task.id,
                    "input": tr.task.input,
                    "output": tr.output[:500],
                    "score": tr.score,
                    "passed": tr.passed,
                    "latency_ms": tr.latency_ms,
                    "steps": tr.steps,
                    "tool_calls": tr.tool_calls,
                    "error": tr.error[:200] if tr.error else "",
                }
                for tr in r.results
            ]
        }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return path
