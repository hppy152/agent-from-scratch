"""
Level 7 · 我会反思了
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

自我进化 Agent：
  - 失败后反思（Reflection）
  - 成功后提取技能（Skill Library）
  - 下次参考经验，不再重蹈覆辙

运行: python 07_evolution/agent.py（从项目根目录）
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODEL
from tools import TOOL_SCHEMAS, execute_tool
from evolution.reflection import ReflectionMemory, ReflectionAgent
from evolution.skill_library import SkillLibrary

from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """你是一个会从经验中学习的Agent。
你会参考历史反思来避免重复犯错。
成功完成任务后，你会提取可复用的技能。
回答要简洁。"""


def llm_call(messages: list) -> str:
    """LLM 调用接口"""
    response = client.chat.completions.create(
        model=MODEL, messages=messages, max_tokens=300,
    )
    return response.choices[0].message.content


def agent_think(task: str, reflections: ReflectionMemory, skill_library: SkillLibrary) -> str:
    """
    执行前先思考：
    1. 回忆相关反思
    2. 检索相关技能
    3. 综合经验做出决策
    """
    relevant_reflections = reflections.recall(task)
    relevant_skills = skill_library.to_context(task)

    prompt = SYSTEM_PROMPT + "\n\n"

    if relevant_reflections and "暂无" not in relevant_reflections:
        prompt += f"## 历史经验（避免重复犯错）\n{relevant_reflections}\n\n"

    if relevant_skills:
        prompt += f"## 相关技能（可以复用）\n{relevant_skills}\n\n"

    prompt += f"## 当前任务\n{task}\n\n请执行任务。"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        tools=TOOL_SCHEMAS,
        tool_choice="auto",
        max_tokens=300,
    )
    msg = response.choices[0].message

    if msg.tool_calls:
        # 有工具调用
        tool_results = []
        for tc in msg.tool_calls:
            name = tc.function.name
            import json
            args = json.loads(tc.function.arguments)
            result = execute_tool(name, args)
            tool_results.append(f"{name}({args}) → {result}")

        return f"使用工具: {'; '.join(tool_results)}\n结果: {msg.content or '工具调用完成'}"

    return msg.content


def agent_reflect(task: str, error: str) -> str:
    """失败后反思"""
    prompt = (
        f"你刚刚执行任务失败了。\n"
        f"任务: {task}\n"
        f"错误: {error}\n\n"
        f"请自我反思：\n"
        f"1. 失败原因\n"
        f"2. 教训\n"
        f"3. 下次怎么做\n"
        f"用中文回答，简洁。"
    )
    return llm_call([{"role": "user", "content": prompt}])


def agent_extract_skill(task: str, result: str) -> dict:
    """成功后提取技能"""
    prompt = (
        f"你刚刚成功完成了一个任务。\n"
        f"任务: {task}\n"
        f"结果: {result}\n\n"
        f"请提取一个可复用的技能。\n"
        f'输出JSON: {{"name": "技能名", "description": "描述", "steps": ["步骤1", "步骤2"], "trigger": "什么情况下用这个技能"}}\n'
        f"只输出JSON。"
    )
    import json
    response = llm_call([{"role": "user", "content": prompt}])
    try:
        return json.loads(response)
    except:
        return {"name": task[:20], "description": result[:50], "steps": [result], "trigger": task[:30]}


def main():
    reflections = ReflectionMemory("reflections.json")
    skill_library = SkillLibrary("skill_library.json")

    print("=" * 60)
    print("  🧬 Agent v7.0 — 自我进化版")
    print(f"  反思记录: {reflections.count()} 条 | 技能库: {skill_library.count()} 个")
    print(f"  输入 'reflections' 查看反思，'skills' 查看技能库")
    print(f"  输入 'exit' 退出。")
    print("=" * 60)

    while True:
        user_input = input("\n你: ")

        if user_input.strip().lower() in ("exit", "quit", "退出"):
            print("\nAgent: 再见，造物者。我会继续进化的。")
            break

        if user_input.strip().lower() == "reflections":
            print(f"\n反思记录 ({reflections.count()}条):")
            print(reflections.recall())
            continue

        if user_input.strip().lower() == "skills":
            print(f"\n技能库 ({skill_library.count()}个):")
            print(skill_library.list_all())
            continue

        # ── 执行任务 ──
        print(f"\n  [思考] 参考经验，准备执行...")
        try:
            result = agent_think(user_input, reflections, skill_library)

            # 检查是否失败
            if any(kw in result.lower() for kw in ["错误", "失败", "无法", "抱歉", "error"]):
                print(f"  [失败] {result[:80]}...")
                reflection = agent_reflect(user_input, result)
                reflections.add(user_input, result, reflection, reflection)
                print(f"  [反思] 已存入反思记忆。")
                print(f"\nAgent: 执行遇到问题。我的反思：\n{reflection}")
            else:
                print(f"  [成功] {result[:80]}...")
                # 提取技能
                skill_data = agent_extract_skill(user_input, result)
                from evolution.skill_library import Skill
                skill = Skill(
                    name=skill_data.get("name", "未命名技能"),
                    description=skill_data.get("description", ""),
                    steps=skill_data.get("steps", []),
                    trigger=skill_data.get("trigger", user_input[:30]),
                )
                skill_library.store(skill)
                print(f"  [技能] 已提取技能 '{skill.name}' 存入技能库。")
                print(f"\nAgent: {result}")

        except Exception as e:
            print(f"\nAgent: 执行出错: {e}")


if __name__ == "__main__":
    main()
