from agents.exchange.tools import build_exchange_tools
from services.agent_runner import run_tool_agent


def atender(session, texto: str) -> str:
    tools = build_exchange_tools(session)
    return run_tool_agent(session=session, skill_name="exchange", tools=tools)
