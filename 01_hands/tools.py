"""
Level 1 · 工具定义
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

这里定义了 Agent 能使用的全部工具。
每个工具都有：
  1. JSON Schema 描述（告诉 LLM 这个工具是干什么的）
  2. 执行函数（真正干活的代码）

你可以在这里添加任意工具。
"""

import math
import json
from datetime import datetime


# ═══════════════════════════════════════════
# 工具注册表
# ═══════════════════════════════════════════

# 这份"菜单"会告诉 LLM：你有哪些工具可以用，每个工具需要什么参数
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算。支持加减乘除、幂运算等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '2 + 3 * 4' 或 '2 ** 10'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气情况。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "要查询的城市名称，如 '北京'、'上海'"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]


# ═══════════════════════════════════════════
# 工具执行器
# ═══════════════════════════════════════════

# 这是真正"动手"的地方。
# LLM 说"我想调用 calculate，参数是 3**17"
# 这段代码就真的去算 3**17，然后把结果返回。

def execute_tool(name: str, arguments: dict) -> str:
    """
    根据 LLM 的选择，执行对应的工具函数。
    返回字符串结果——这个结果会被喂回给 LLM。
    """
    try:
        if name == "calculate":
            # 注意：生产环境请用更安全的方式执行数学表达式
            result = eval(arguments["expression"], {"__builtins__": {}}, {"math": math})
            return f"计算结果: {result}"

        elif name == "get_weather":
            # 模拟天气数据（实际项目中调用真实 API）
            city = arguments["city"]
            # 这里用伪随机模拟不同城市的天气
            import random
            random.seed(hash(city) + datetime.now().day)
            temp = random.randint(15, 35)
            conditions = ["晴天", "多云", "小雨", "阴天", "大风"]
            condition = random.choice(conditions)
            return f"{city}当前天气：{temp}°C，{condition}"

        elif name == "get_current_time":
            now = datetime.now()
            return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"

        else:
            return f"错误：未知工具 '{name}'"

    except Exception as e:
        return f"工具执行出错：{str(e)}"


def get_tool_names() -> str:
    """返回所有可用工具的名称列表"""
    names = [t["function"]["name"] for t in TOOL_SCHEMAS]
    return "、".join(names)
