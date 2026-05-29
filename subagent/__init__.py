"""
SubAgent — 子 Agent 系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

核心概念：
  - SubAgent: 独立的 LLM 会话，专注处理一个任务
  - SubAgentOrchestrator: 父 Agent，能动态分发任务给子 Agent
  - delegate_task: 核心方法，把任务委派给子 Agent
"""

try:
    from .core import SubAgent, SubAgentResponse
    from .orchestrator import SubAgentOrchestrator, DelegatePlan
except ImportError:
    from core import SubAgent, SubAgentResponse
    from orchestrator import SubAgentOrchestrator, DelegatePlan

__all__ = [
    "SubAgent", "SubAgentResponse",
    "SubAgentOrchestrator", "DelegatePlan",
]
