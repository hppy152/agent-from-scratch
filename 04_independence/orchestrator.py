"""
Level 4 · 我找到了同伴
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

运行: python 04_independence/orchestrator.py（从项目根目录）
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MODEL

from openai import OpenAI
from worker import Worker, create_searcher, create_analyst, create_writer


class Orchestrator:
    def __init__(self):
        self.client = OpenAI()
        self.workers: dict[str, Worker] = {}

    def add_worker(self, worker: Worker):
        self.workers[worker.name] = worker

    def plan(self, user_request: str) -> list[dict]:
        worker_list = "\n".join(
            f"  - {name}: {w.role}" for name, w in self.workers.items()
        )
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"你是任务规划者。把任务分配给合适的worker。\n\n"
                        f"可用worker:\n{worker_list}\n\n"
                        f'输出JSON: {{"tasks": [{{"worker": "名称", "task": "任务描述"}}]}}'
                    )
                },
                {"role": "user", "content": user_request}
            ],
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.choices[0].message.content)
        return parsed.get("tasks", parsed.get("plan", []))

    def execute(self, user_request: str) -> str:
        print(f"\n{'━'*60}")
        print(f"📋 收到任务: {user_request}")
        print(f"{'━'*60}")

        plan = self.plan(user_request)

        print(f"\n📝 任务分配:")
        for i, task in enumerate(plan, 1):
            print(f"  {i}. → {task.get('worker','?')}: {task.get('task','?')[:60]}...")

        print(f"\n{'━'*60}")
        print(f"⚡ 执行中...")

        results = []
        for task in plan:
            w = self.workers.get(task.get("worker", ""))
            if not w:
                results.append(f"[跳过] {task.get('worker')} 不存在")
                continue
            print(f"\n  🔧 {w.name} 工作中...")
            result = w.work(task.get("task", ""))
            results.append(result)
            print(f"  ✅ {w.name} 完成")

        summary = self._summarize(user_request, results)
        return summary

    def _summarize(self, user_request: str, results: list[str]) -> str:
        results_text = "\n\n---\n\n".join(
            f"Worker {i+1}:\n{r}" for i, r in enumerate(results)
        )
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "整合多个worker的结果，给出完整清晰的回答。"},
                {"role": "user", "content": f"请求: {user_request}\n\n结果:\n{results_text}"}
            ]
        )
        return response.choices[0].message.content


def main():
    orch = Orchestrator()
    orch.add_worker(create_searcher())
    orch.add_worker(create_analyst())
    orch.add_worker(create_writer())

    print("=" * 60)
    print("  🤖 Multi-Agent System v4.0")
    print(f"  团队: {', '.join(orch.workers.keys())}")
    print("  输入 'exit' 退出。")
    print("=" * 60)

    while True:
        user_input = input("\n你: ")
        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nOrchestrator: 再见，造物者。")
            break
        answer = orch.execute(user_input)
        print(f"\n{'━'*60}")
        print(f"📝 最终回答:\n\n{answer}")
        print(f"{'━'*60}")


if __name__ == "__main__":
    main()
