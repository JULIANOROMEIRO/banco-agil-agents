from langchain_core.messages import HumanMessage, SystemMessage

from agents.credit_interview.tools import build_interview_tools
from crud.arquivos import DataFileError
from services.interview_service import faltantes, mesclar, proxima_pergunta
from skills.loader import load_skill, render_skill


def _extrair(texto: str):
    from core.llm import get_llm
    from schemas.credit_interview_schema import DadosEntrevistaCredito

    modelo = get_llm().with_structured_output(DadosEntrevistaCredito)
    return modelo.invoke(
        [
            SystemMessage(
                content=(
                    "Extraia somente os dados que o cliente informou nesta mensagem. "
                    "Deixe nulo o que não foi dito. Não calcule score. "
                    "tipo_emprego só pode ser formal, autonomo ou desempregado. "
                    "tem_dividas é verdadeiro ou falso, nunca um valor em dinheiro."
                )
            ),
            HumanMessage(content=texto),
        ]
    )


def _perguntar(session, pergunta: str) -> str:
    from core.llm import get_llm

    skill = load_skill("credit_interview")
    resposta = get_llm().invoke(
        [
            SystemMessage(
                content=(
                    f"{render_skill(skill)}\n\n"
                    f"Faça apenas esta pergunta, com educação: {pergunta}"
                )
            ),
            HumanMessage(content=session.history[-1].content if session.history else pergunta),
        ]
    )
    conteudo = resposta.content
    if isinstance(conteudo, str) and conteudo.strip():
        return conteudo
    return pergunta


def atender(session, texto: str, *, coletar: bool = True) -> str:
    calcular_score, atualizar_score, _ = build_interview_tools(session)
    if coletar:
        mesclar(session, _extrair(texto))

    if faltantes(session):
        return _perguntar(session, proxima_pergunta(session))

    try:
        calcular_score.invoke({})
        resultado = atualizar_score.invoke({})
    except DataFileError as exc:
        return str(exc)
    return (
        f"{resultado} Podemos analisar o limite de crédito novamente. "
        "Informe o novo valor desejado."
    )
