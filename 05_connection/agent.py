"""
Level 5 · 我学会了连接世界
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Skill Loader（知识）  +  MCP Client（工具）  +  ReAct 循环
        ↓                       ↓                     ↓
    "怎么做"的 SOP         "连什么"的标准协议     推理-行动-观察

运行: python 05_connection/agent.py（从项目根目录）
"""

import json
import sys
import os

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
# 当前目录（mcp_client, skill_loader 所在）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODEL
from mcp_client import MCPClient
from skill_loader import SkillLoader

from openai import OpenAI


class AgentV5:
    """
    支持 Skills + MCP 的完整 Agent。

    架构:
      用户输入
        → Skill Loader 匹配相关知识
        → 注入 system prompt
        → ReAct 循环（LLM + MCP 工具）
        → 最终回答
    """

    def __init__(self):
        self.client = OpenAI()
        self.mcp_clients: list[MCPClient] = []
        self.skill_loader = SkillLoader(
            os.path.join(ROOT, "skills")
        )
        self.all_tools: list[dict] = []

    def connect_mcp(self, command: str, args: list[str] = None, name: str = ""):
        """连接一个 MCP Server"""
        mcp = MCPClient(command, args, name)
        if mcp.proc:
            self.mcp_clients.append(mcp)
            # 把这个 Server 的工具合并到总工具列表
            self.all_tools.extend(mcp.get_tool_schemas())
            print(f"  ✅ MCP Server 已连接: {mcp.name}")
            print(f"     工具: {[t['name'] for t in mcp.tools]}")
        else:
            print(f"  ❌ MCP Server 连接失败: {name or command}")

    def _find_mcp(self, tool_name: str) -> MCPClient | None:
        """找到拥有某个工具的 MCP Client"""
        for mcp in self.mcp_clients:
            for tool in mcp.tools:
                if tool["name"] == tool_name:
                    return mcp
        return None

    def chat(self, user_input: str) -> str:
        """
        核心循环：
        1. 匹配 Skills → 注入知识
        2. ReAct 循环 → 调用 MCP 工具
        3. 返回最终回答
        """

        # ── Step 1: 匹配并加载 Skills ──────
        matched = self.skill_loader.match(user_input)
        skill_text = self.skill_loader.load(matched)

        if matched:
            print(f"  [Skill] 匹配: {', '.join(matched)}")

        # ── Step 2: 构建带知识的 System Prompt ──
        system_prompt = (
            "你是一个拥有技能和工具的智能Agent。\n"
            "你通过MCP协议连接外部工具，通过Skill获取专业知识。\n"
            "回答要简洁、准确、有条理。"
        )
        if skill_text:
            system_prompt += f"\n\n## 相关技能知识\n\n{skill_text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        # ── Step 3: ReAct 循环（带 MCP 工具）──
        for step in range(10):
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=self.all_tools if self.all_tools else None,
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)

                    # 找到对应的 MCP Server 并调用
                    mcp = self._find_mcp(name)
                    if mcp:
                        print(f"  → MCP调用: {name}({args})")
                        result = mcp.call_tool(name, args)
                        print(f"  → 返回: {result[:80]}...")
                    else:
                        result = f"工具 '{name}' 不存在"

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
            else:
                # LLM 给出最终回答
                return msg.content

        return "思考步数超限，无法完成任务。"

    def close(self):
        """关闭所有 MCP 连接"""
        for mcp in self.mcp_clients:
            mcp.close()


def main():
    agent = AgentV5()

    print("=" * 60)
    print("  🌍 Agent v5.0 — 连接世界版")
    print(f"  已加载 {len(agent.skill_loader.skills)} 个技能")
    print(f"  输入 'skills' 查看技能列表")
    print(f"  输入 'exit' 退出。")
    print("=" * 60)

    # ── 连接内置 MCP Server ──────────────
    server_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "simple_mcp_server.py"
    )
    agent.connect_mcp(
        "python3", [server_script],
        name="simple-mcp-server"
    )

    print(f"\n  可用 MCP 工具: {[t['function']['name'] for t in agent.all_tools]}")
    print()

    try:
        while True:
            user_input = input("你: ")

            if user_input.strip().lower() in ("exit", "quit", "退出"):
                print("\nAgent: 再见，造物者。世界很大，我已经准备好了。")
                break

            if user_input.strip().lower() == "skills":
                print(f"\n可用技能:\n{agent.skill_loader.list_all()}")
                continue

            response = agent.chat(user_input)
            print(f"\nAgent: {response}\n")

    finally:
        agent.close()


if __name__ == "__main__":
    main()
