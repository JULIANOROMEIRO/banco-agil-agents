import pytest

from services import session_service

CPF = "11111111111"
NASCIMENTO = "15/05/1990"


@pytest.mark.asyncio
async def test_health(async_client):
    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["llm_configured"] is False


@pytest.mark.asyncio
async def test_cria_sessao(async_client):
    response = await async_client.post("/api/v1/sessions")

    corpo = response.json()
    assert response.status_code == 200
    assert corpo["session_id"]
    assert corpo["finished"] is False


@pytest.mark.asyncio
async def test_autenticacao_correta(async_client):
    criada = await async_client.post("/api/v1/sessions")
    session_id = criada.json()["session_id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"message": f"CPF {CPF} nascimento {NASCIMENTO}"},
    )

    corpo = response.json()
    assert response.status_code == 200
    assert corpo["session"]["authenticated"] is True
    assert corpo["session"]["cpf"] == CPF
    assert "Ana Lima" in corpo["reply"]


@pytest.mark.asyncio
async def test_terceira_falha_encerra(async_client):
    criada = await async_client.post("/api/v1/sessions")
    session_id = criada.json()["session_id"]

    for _ in range(3):
        response = await async_client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"message": "000.000.000-00 01/01/1990"},
        )

    corpo = response.json()
    assert corpo["session"]["auth_attempts"] == 3
    assert corpo["session"]["finished"] is True


@pytest.mark.parametrize(
    "frase",
    [
        "quero encerrar",
        "pode finalizar meu atendimento",
        "tchau",
    ],
)
def test_frase_de_encerramento_termina_o_atendimento(frase):
    session = session_service.criar()
    session.authenticated = True
    session.cpf = CPF

    resposta = session_service.enviar_mensagem(session.session_id, frase)

    assert resposta.reply == "Atendimento encerrado."
    assert session.finished is True


@pytest.mark.parametrize(
    "frase",
    [
        "fim de semana",
        "se eu sair do emprego meu limite diminui?",
        "enfim, quero consultar meu limite",
    ],
)
def test_frase_semelhante_nao_encerra_o_atendimento(frase, monkeypatch):
    monkeypatch.setattr(
        "services.orchestrator.credit.atender",
        lambda session, texto: "Consulta em andamento.",
    )
    session = session_service.criar()
    session.authenticated = True
    session.cpf = CPF
    session.active_agent = "credit"

    resposta = session_service.enviar_mensagem(session.session_id, frase)

    assert session.finished is False
    assert resposta.reply == "Consulta em andamento."
