"""
Level 4 · 我找到了同伴
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

多 Agent 协作系统：
  - Orchestrator（指挥官）：理解需求、分配任务、汇总结果
  - Worker（专家）：各自的专业领域

运行: python 04_independence/orchestrator.py（从项目根目录）
"""

import json
import sys
import os

# 从项目根目录导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 当前目录（worker.py 所在位置）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from worker import Worker, create_searcher, create_analyst, create_writer


# ═══════════════════════════════════════════
# Orchestrator：指挥官
# ═══════════════════════════════════════════

class Orchestrator:
    """
    指挥官 Agent。
    它不亲自干活——它负责思考、规划、调度、汇总。
    就像一个项目经理：知道需要什么人，把活分下去，最后整合结果。
    """

    def __init__(self):
        self.client = OpenAI()
        self.workers: dict[str, Worker] = {}

    def add_worker(self, worker: Worker):
        """招募一个专业 worker"""
        self.workers[worker.name] = worker

    def plan(self, user_request: str) -> list[dict]:
        """
        让 LLM 规划任务分配。
        输入用户请求，输出任务列表：[{"worker": "xxx", "task": "xxx"}]
        """

        worker_list = "\n".join(
            f"  - {name}: {w.role}" for name, w in self.workers.items()
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"你是任务规划者。根据用户请求，把任务分配给合适的worker。\n\n"
                        f"可用的worker:\n{worker_list}\n\n"
                        f"输出JSON数组，每个元素格式: {{\"worker\": \"worker名称\", \"task\": \"具体任务描述\"}}\n"
                        f"只输出JSON，不要其他内容。"
                    )
                },
                {"role": "user", "content": user_request}
            ],
            response_format={"type": "json_object"},
        )

        result = response.choices[0].message.content
        parsed = json.loads(result)

        if isinstance(parsed, dict):
            tasks = parsed.get("tasks", parsed.get("plan", []))
        else:
            tasks = parsed

        return tasks

    def execute(self, user_request: str) -> str:
        """
        完整流程：规划 → 执行 → 汇总
        """
        print(f"\n{'━'*60}")
        print(f"📋 Orchestrator 收到任务: {user_request}")
        print(f"{'━'*60}")

        plan = self.plan(user_request)

        print(f"\n📝 任务分配:")
        for i, task in enumerate(plan, 1):
            worker_name = task.get("worker", "unknown")
            task_desc = task.get("task", "unknown")
            print(f"  {i}. → {worker_name}: {task_desc[:60]}...")

        print(f"\n{'━'*60}")
        print(f"⚡ 开始执行...")
        print(f"{'━'*60}")

        results = []
        for task in plan:
            worker_name = task.get("worker", "unknown")
            task_desc = task.get("task", "unknown")

            worker = self.workers.get(worker_name)
            if not worker:
                print(f"  ⚠️ Worker '{worker_name}' 不存在，跳过")
                results.append(f"[跳过] Worker '{worker_name}' 不存在")
                continue

            print(f"\n  🔧 {worker.name} 开始工作...")
            result = worker.work(task_desc)
            results.append(result)
            print(f"  ✅ {worker.name} 完成！")
            print(f"     摘要: {result[:80]}...")

        print(f"\n{'━'*60}")
        print(f"📊 汇总结果...")
        print(f"{'━'*60}")

        summary = self._summarize(user_request, results)
        return summary

    def _summarize(self, user_request: str, results: list[str]) -> str:
        """用 LLM 把多个 worker 的结果整合成一个完整回答"""

        results_text = "\n\n---\n\n".join(
            f"Worker {i+1} 的结果:\n{r}" for i, r in enumerate(results)
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是结果汇总者。\n"
                        "把多个worker的调研结果整合成一个完整、清晰的回答。\n"
                        "给出结论和建议。"
                    )
                },
                {
                    "role": "user",
                    "content": f"原始请求: {user_request}\n\n各worker的结果:\n{results_text}"
                }
            ]
        )

        return response.choices[0].message.content


# ═══════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════

def main():
    orch = Orchestrator()
    orch.add_worker(create_searcher())
    orch.add_worker(create_analyst())
    orch.add_worker(create_writer())

    print("=" * 60)
    print("  🤖 Multi-Agent System v4.0")
    print(f"  团队成员: {', '.join(orch.workers.keys())}")
    print("  输入 'exit' 退出。")
    print("=" * 60)

    while True:
        user_input = input("\n你: ")

        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nOrchestrator: 团队解散。再见，造物者。")
            break

        answer = orch.execute(user_input)
        print(f"\n{'━'*60}")
        print(f"📝 最终回答:\n\n{answer}")
        print(f"{'━'*60}")


if __name__ == "__main__":
    main()
