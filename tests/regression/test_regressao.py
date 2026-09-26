from pathlib import Path

import pytest
import yaml

from services import session_service
from tests.fakes import FakeLLM

CENARIOS = Path(__file__).with_name("cenarios.yaml")


def _autenticada():
    session = session_service.criar()
    session.authenticated = True
    session.cpf = "11111111111"
    return session


@pytest.mark.parametrize("cenario", yaml.safe_load(CENARIOS.read_text(encoding="utf-8"))["cenarios"])
def test_roteamento(cenario, monkeypatch):
    monkeypatch.setattr("core.llm.get_llm", lambda: FakeLLM())
    session = _autenticada()

    session_service.enviar_mensagem(session.session_id, cenario["mensagem"])

    assert session.active_agent == cenario["active_agent"]


def test_cotacao_no_meio_do_credito_troca_de_agente(monkeypatch):
    monkeypatch.setattr("core.llm.get_llm", lambda: FakeLLM())
    session = _autenticada()

    session_service.enviar_mensagem(session.session_id, "Quero aumentar meu limite")
    assert session.active_agent == "credit"

    session_service.enviar_mensagem(session.session_id, "Quero a cotação do dólar")
    assert session.active_agent == "exchange"


def test_valor_do_limite_nao_troca_de_agente(monkeypatch):
    monkeypatch.setattr("core.llm.get_llm", lambda: FakeLLM())
    session = _autenticada()
    session.active_agent = "credit"

    session_service.enviar_mensagem(session.session_id, "30000")

    assert session.active_agent == "credit"
