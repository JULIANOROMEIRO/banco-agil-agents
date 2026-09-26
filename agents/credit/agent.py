from agents.credit.tools import build_credit_tools
from services.agent_runner import run_tool_agent

_ACEITE = {"sim", "aceito", "pode ser", "quero sim", "vamos"}


def _resposta_da_oferta(session, texto: str) -> str | None:
    if not session.awaiting_interview_confirmation:
        return None
    normalizado = texto.strip().lower()
    if normalizado.startswith("não") or normalizado.startswith("nao"):
        return "recusa"
    if normalizado in _ACEITE or normalizado.startswith("sim"):
        return "aceita"
    return None


def atender(session, texto: str) -> str:
    oferta = _resposta_da_oferta(session, texto)
    if oferta == "aceita":
        session.awaiting_interview_confirmation = False
        session.active_agent = "credit_interview"
        from agents.credit_interview.agent import atender as atender_entrevista

        return atender_entrevista(session, texto, coletar=False)
    if oferta == "recusa":
        session.awaiting_interview_confirmation = False
        return "Tudo bem. Seguimos sem a entrevista de crédito."

    tools = build_credit_tools(session)
    resposta = run_tool_agent(session=session, skill_name="credit", tools=tools)
    if session.awaiting_interview_confirmation:
        return (
            f"{resposta} Posso fazer uma entrevista rápida para recalcular o seu score. "
            "Você aceita?"
        )
    return resposta
