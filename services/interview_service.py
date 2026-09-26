"""Entrevista de crédito. O cálculo do score é determinístico."""

from crud import crud_clientes

CAMPOS = ("renda_mensal", "tipo_emprego", "despesas", "dependentes", "tem_dividas")
PESO_RENDA = 30
PESO_EMPREGO = {
    "formal": 300,
    "autonomo": 200,
    "desempregado": 0,
}
PERGUNTAS = {
    "renda_mensal": "Qual é a sua renda mensal?",
    "tipo_emprego": "Qual é o seu tipo de emprego: formal, autônomo ou desempregado?",
    "despesas": "Qual é o valor das suas despesas fixas mensais?",
    "dependentes": "Quantos dependentes você possui?",
    "tem_dividas": "Você possui dívidas ativas?",
}


def normalizar_emprego(valor: str | None) -> str | None:
    if valor is None:
        return None
    texto = str(valor).strip().lower()
    for origem, destino in (("á", "a"), ("â", "a"), ("ã", "a"), ("ô", "o"), ("ó", "o"), ("é", "e")):
        texto = texto.replace(origem, destino)
    if texto in PESO_EMPREGO:
        return texto
    return None


def _peso_dependentes(dependentes: int) -> int:
    if dependentes <= 0:
        return 100
    if dependentes == 1:
        return 80
    if dependentes == 2:
        return 60
    return 30


def calcular_score(
    renda_mensal: float,
    tipo_emprego: str,
    despesas: float,
    dependentes: int,
    tem_dividas: bool,
) -> int:
    if renda_mensal < 0:
        raise ValueError("Renda mensal não pode ser negativa.")
    if despesas < 0:
        raise ValueError("Despesas não podem ser negativas.")
    if dependentes < 0:
        raise ValueError("Dependentes não podem ser negativos.")
    emprego = normalizar_emprego(tipo_emprego) or ""
    bruto = (
        (renda_mensal / (despesas + 1)) * PESO_RENDA
        + PESO_EMPREGO.get(emprego, 0)
        + _peso_dependentes(dependentes)
        + (-100 if tem_dividas else 100)
    )
    return max(0, min(1000, round(bruto)))


def mesclar(session, campos) -> None:
    for nome in CAMPOS:
        valor = getattr(campos, nome)
        if nome == "tipo_emprego":
            valor = normalizar_emprego(valor)
        if valor is None or valor == "":
            continue
        session.interview_data[nome] = valor


def faltantes(session) -> list[str]:
    return [
        nome
        for nome in CAMPOS
        if session.interview_data.get(nome) in (None, "")
    ]


def calcular_score_da_sessao(session) -> int:
    dados = session.interview_data
    return calcular_score(
        renda_mensal=float(dados["renda_mensal"]),
        tipo_emprego=str(dados["tipo_emprego"]),
        despesas=float(dados["despesas"]),
        dependentes=int(dados["dependentes"]),
        tem_dividas=bool(dados["tem_dividas"]),
    )


def atualizar_score_cliente(session, score: int) -> int:
    score_valido = max(0, min(1000, int(score)))
    crud_clientes.atualizar_score(session.cpf, score_valido)
    session.active_agent = "credit"
    return score_valido


def proxima_pergunta(session) -> str:
    pendentes = faltantes(session)
    if not pendentes:
        return "Entrevista completa."
    return PERGUNTAS[pendentes[0]]
