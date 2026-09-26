"""Consulta de cotação. Converte erros da integração em texto para o cliente."""

from integrations.exchange_client import ExchangeError, consultar_cotacao as consultar_na_api


def consultar_cotacao(moeda: str) -> str:
    try:
        dados = consultar_na_api(moeda)
    except ExchangeError as exc:
        return exc.mensagem
    return f"1 {dados['moeda']} = {dados['cotacao_brl']:.4f} BRL."
