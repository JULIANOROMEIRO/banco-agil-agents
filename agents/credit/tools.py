from langchain_core.tools import tool

from services import credit_service


def build_credit_tools(session):
    @tool
    def consultar_limite(cpf: str) -> str:
        """Consulta o limite de crédito e o score do cliente."""
        return credit_service.consultar_limite(cpf).mensagem

    @tool
    def solicitar_aumento_limite(cpf: str, novo_limite: float) -> str:
        """Registra a solicitação e informa se o aumento foi aprovado ou rejeitado."""
        resultado = credit_service.solicitar_aumento_limite(cpf, novo_limite)
        if resultado.status_pedido == "rejeitado":
            session.awaiting_interview_confirmation = True
        return resultado.mensagem

    @tool
    def finalizar_atendimento() -> str:
        """Encerra o atendimento atual."""
        session.finished = True
        return "Atendimento encerrado."

    return [consultar_limite, solicitar_aumento_limite, finalizar_atendimento]
