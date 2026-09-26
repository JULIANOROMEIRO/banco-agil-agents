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
