"""Regras de crédito. Aprovação e rejeição acontecem aqui, nunca no LLM."""

from datetime import datetime, timezone

from fastapi import HTTPException

from crud import crud_clientes, crud_score, crud_solicitacoes
from schemas.cliente_schema import LimiteConsulta, SolicitacaoLimite, SolicitacaoResultado


def consultar_limite(cpf: str) -> LimiteConsulta:
    cliente = crud_clientes.buscar_cliente(cpf)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    mensagem = (
        f"O limite atual de {cliente.nome} é R$ {cliente.limite_atual:.2f}. "
        f"Score: {cliente.score}."
    )
    return LimiteConsulta(
        nome=cliente.nome,
        cpf=cliente.cpf,
        limite_atual=cliente.limite_atual,
        score=cliente.score,
        mensagem=mensagem,
    )


def solicitar_aumento_limite(cpf: str, novo_limite: float) -> SolicitacaoResultado:
    cliente = crud_clientes.buscar_cliente(cpf)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    faixa = crud_score.buscar_faixa_score(cliente.score)
    limite_maximo = faixa.limite_maximo if faixa else 0

    if faixa is None:
        status = "rejeitado"
        mensagem = "Não há faixa de score para este cliente."
    elif novo_limite <= cliente.limite_atual:
        status = "rejeitado"
        mensagem = "O novo limite precisa ser maior que o limite atual."
    elif novo_limite <= faixa.limite_maximo:
        status = "aprovado"
        crud_clientes.atualizar_limite(cpf, novo_limite)
        mensagem = (
            f"Solicitação aprovada. O novo limite de {cliente.nome} é R$ {novo_limite:.2f}."
        )
    else:
        status = "rejeitado"
        mensagem = (
            f"Solicitação rejeitada. Para o score {cliente.score}, "
            f"o limite máximo é R$ {faixa.limite_maximo:.2f}."
        )

    crud_solicitacoes.salvar_solicitacao(
        SolicitacaoLimite(
            cpf_cliente=crud_clientes.somente_digitos(cpf),
            data_hora_solicitacao=datetime.now(timezone.utc).isoformat(),
            limite_atual=cliente.limite_atual,
            novo_limite_solicitado=novo_limite,
            status_pedido=status,
        )
    )
    return SolicitacaoResultado(
        status_pedido=status,
        limite_atual=cliente.limite_atual,
        novo_limite_solicitado=novo_limite,
        limite_maximo=limite_maximo,
        mensagem=mensagem,
    )
