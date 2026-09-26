from langchain_core.tools import tool

from services import interview_service


def build_interview_tools(session):
    @tool
    def calcular_score() -> int:
        """Calcula o score com os dados da entrevista. O valor fica entre 0 e 1000."""
        return interview_service.calcular_score_da_sessao(session)

    @tool
    def atualizar_score() -> str:
        """Grava no cadastro o score calculado com os dados da entrevista."""
        score = interview_service.calcular_score_da_sessao(session)
        gravado = interview_service.atualizar_score_cliente(session, score)
        return f"Score atualizado para {gravado}."

    @tool
    def finalizar_atendimento() -> str:
        """Encerra o atendimento atual."""
        session.finished = True
        return "Atendimento encerrado."

    return calcular_score, atualizar_score, finalizar_atendimento
