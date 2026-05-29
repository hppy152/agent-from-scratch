"""
共享工具模块
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

所有 Level 共用的工具定义和执行器。
这样每个 Level 的 agent.py 都可以从根目录直接运行。

用法（从项目根目录）:
    python 00_awakening/agent.py
    python 01_hands/agent.py
"""

import ast
import operator
import json
import math
import random
from datetime import datetime


# ═══════════════════════════════════════════
# 安全的数学计算（替代 eval）
# ═══════════════════════════════════════════

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression: str) -> float:
    """
    安全地计算数学表达式，不使用 eval()。
    只支持基本运算：+ - * / // % **
    """
    tree = ast.parse(expression, mode='eval')

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            return SAFE_OPERATORS[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            return SAFE_OPERATORS[type(node.op)](operand)
        else:
            raise ValueError(f"不支持的表达式: {ast.dump(node)}")

    return _eval(tree)


# ═══════════════════════════════════════════
# 工具 Schema（告诉 LLM 有哪些工具可用）
# ═══════════════════════════════════════════

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行安全的数学计算。支持加减乘除、幂运算等。",
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

def execute_tool(name: str, arguments: dict) -> str:
    """
    根据 LLM 的选择，执行对应的工具函数。
    返回字符串结果——这个结果会被喂回给 LLM。
    """
    try:
        if name == "calculate":
            result = safe_calculate(arguments["expression"])
            return f"计算结果: {result}"

        elif name == "get_weather":
            city = arguments["city"]
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
