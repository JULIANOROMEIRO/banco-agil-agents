from services import credit_service
from crud import crud_clientes


def test_consulta_de_limite():
    consulta = credit_service.consultar_limite("11111111111")

    assert consulta.limite_atual == 20000
    assert consulta.score == 850
    assert consulta.nome == "Ana Lima"


def test_aumento_aprovado():
    resultado = credit_service.solicitar_aumento_limite("11111111111", 30000)

    assert resultado.status_pedido == "aprovado"
    assert crud_clientes.buscar_cliente("11111111111").limite_atual == 30000


def test_aumento_rejeitado():
    resultado = credit_service.solicitar_aumento_limite("33333333333", 5000)

    cliente = crud_clientes.buscar_cliente("33333333333")
    assert resultado.status_pedido == "rejeitado"
    assert cliente.limite_atual == 500
    assert "rejeitada" in resultado.mensagem
