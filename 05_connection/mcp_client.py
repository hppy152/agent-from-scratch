"""
MCP Client — 连接 MCP Server 的客户端
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

通过 JSON-RPC 2.0 与 MCP Server 通信（stdio 模式）。
"""

import json
import subprocess


class MCPClient:
    """连接一个 MCP Server，发现并调用它的工具"""

    def __init__(self, command: str, args: list[str] = None, name: str = ""):
        self.name = name or command
        self.tools = []
        self._req_id = 0

        try:
            self.proc = subprocess.Popen(
                [command] + (args or []),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self._initialize()
        except FileNotFoundError:
            print(f"  ⚠️ 无法启动 MCP Server: {command}")
            self.proc = None

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _send_request(self, method: str, params: dict = None) -> dict:
        """发送 JSON-RPC 请求并等待响应"""
        if not self.proc:
            return {"error": "Server 未启动"}

        req_id = self._next_id()
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }

        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()

        response_line = self.proc.stdout.readline()
        if not response_line:
            return {"error": "Server 无响应"}

        return json.loads(response_line.strip())

    def _send_notification(self, method: str, params: dict = None):
        """发送通知（不需要响应）"""
        if not self.proc:
            return

        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }

        self.proc.stdin.write(json.dumps(notification) + "\n")
        self.proc.stdin.flush()

    def _initialize(self):
        """握手：初始化连接，获取工具列表"""
        resp = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "agent-from-scratch", "version": "1.0"}
        })

        if "error" in resp:
            print(f"  ⚠️ MCP 握手失败: {resp['error']}")
            return

        # 发送通知（不需要等响应）
        self._send_notification("notifications/initialized")

        # 获取工具列表
        tools_resp = self._send_request("tools/list")
        self.tools = tools_resp.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> str:
        """调用 Server 上的一个工具"""
        if not self.proc:
            return "MCP Server 未连接"

        resp = self._send_request("tools/call", {
            "name": name,
            "arguments": arguments,
        })

        if "error" in resp:
            return f"工具调用错误: {resp['error']}"

        result = resp.get("result", {})
        contents = result.get("content", [])
        return "\n".join(c.get("text", str(c)) for c in contents)

    def get_tool_schemas(self) -> list[dict]:
        """把 MCP 工具转成 OpenAI Function Calling 格式"""
        schemas = []
        for tool in self.tools:
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {
                        "type": "object", "properties": {}
                    }),
                }
            })
        return schemas

    def close(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()

    def __repr__(self):
        tool_names = [t["name"] for t in self.tools]
        return f"MCPClient({self.name}, tools={tool_names})"
