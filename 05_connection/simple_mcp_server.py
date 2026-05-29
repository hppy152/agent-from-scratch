#!/usr/bin/env python3
"""
最简 MCP Server — 用于教学和测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

这是一个 MCP (Model Context Protocol) Server 的最小实现。
它通过 stdio 接收 JSON-RPC 请求，暴露几个简单工具。

这个文件本身就是一个 MCP Server —— 你学到的所有知识，
都凝缩在这 100 行代码里。

运行: python simple_mcp_server.py
协议: JSON-RPC 2.0 over stdio
"""

import sys
import json
import math
import random
from datetime import datetime
from urllib.request import urlopen


# ═══════════════════════════════════════════
# 工具定义：这个 Server 能提供什么能力
# ═══════════════════════════════════════════

TOOLS = [
    {
        "name": "calculate",
        "description": "安全地执行数学计算，支持加减乘除、幂运算等",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2 + 3 * 4'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_weather",
        "description": "查询指定城市的当前天气",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "web_search",
        "description": "搜索网页信息（模拟搜索）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_time",
        "description": "获取当前日期和时间",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
]


# ═══════════════════════════════════════════
# 工具执行器：真正干活的地方
# ═══════════════════════════════════════════

def execute_tool(name: str, arguments: dict) -> str:
    """执行一个工具，返回结果文本"""
    if name == "calculate":
        try:
            # 安全计算（不用 eval）
            import ast, operator
            ops = {
                ast.Add: operator.add, ast.Sub: operator.sub,
                ast.Mult: operator.mul, ast.Div: operator.truediv,
                ast.Pow: operator.pow, ast.Mod: operator.mod,
            }
            tree = ast.parse(arguments["expression"], mode='eval')
            def _eval(node):
                if isinstance(node, ast.Expression): return _eval(node.body)
                elif isinstance(node, ast.Constant): return node.value
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](_eval(node.left), _eval(node.right))
                raise ValueError(f"不支持: {ast.dump(node)}")
            return str(_eval(tree))
        except Exception as e:
            return f"计算错误: {e}"

    elif name == "get_weather":
        city = arguments["city"]
        random.seed(hash(city) + datetime.now().day)
        temp = random.randint(15, 35)
        cond = random.choice(["晴天", "多云", "小雨", "阴天", "大风"])
        return f"{city}当前天气：{temp}°C，{cond}"

    elif name == "web_search":
        query = arguments["query"]
        return (
            f"搜索 '{query}' 的结果：\n"
            f"1. {query}的最新资讯和分析\n"
            f"2. 关于{query}的社区讨论\n"
            f"3. {query}入门教程和最佳实践"
        )

    elif name == "get_time":
        now = datetime.now()
        return now.strftime("当前时间：%Y年%m月%d日 %H:%M:%S")

    return f"未知工具: {name}"


# ═══════════════════════════════════════════
# JSON-RPC 处理器：MCP 协议的核心
# ═══════════════════════════════════════════

def handle_request(request: dict) -> dict:
    """
    处理一个 JSON-RPC 请求，返回响应。
    MCP 协议只有几个关键方法：
      - initialize: 握手
      - tools/list: 列出可用工具
      - tools/call: 调用工具
    """
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    # ── 握手：客户端说"你好"，我们返回能力 ──
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "simple-mcp-server",
                    "version": "1.0.0"
                }
            }
        }

    # ── 初始化完成通知（不需要回复）──
    elif method == "notifications/initialized":
        return None  # 通知不需要响应

    # ── 列出工具 ──
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        }

    # ── 调用工具 ──
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = execute_tool(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": result}]
            }
        }

    # ── 未知方法 ──
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"未知方法: {method}"}
        }


# ═══════════════════════════════════════════
# 主循环：从 stdin 读请求，往 stdout 写响应
# ═══════════════════════════════════════════

def main():
    """MCP Server 主循环 — 读一行 JSON，处理，返回结果"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError as e:
            error_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"JSON 解析错误: {e}"}
            }
            sys.stdout.write(json.dumps(error_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
