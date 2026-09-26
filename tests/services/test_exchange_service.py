import httpx

from services import exchange_service


class _Resposta:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {"rates": {"BRL": 5.25}, "date": "2026-09-24"}

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://api.frankfurter.app/latest")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("erro", request=request, response=response)

    def json(self):
        return self._payload


class _Cliente:
    def __init__(self, resposta=None, erro=None):
        self.resposta = resposta or _Resposta()
        self.erro = erro

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, url, params=None):
        if self.erro:
            raise self.erro
        return self.resposta


def test_cotacao(monkeypatch):
    monkeypatch.setattr("integrations.exchange_client.httpx.Client", lambda *args, **kwargs: _Cliente())

    texto = exchange_service.consultar_cotacao("usd")

    assert texto == "1 USD = 5.2500 BRL."


def test_timeout_da_api_de_cambio(monkeypatch):
    cliente = lambda *args, **kwargs: _Cliente(erro=httpx.TimeoutException("tempo esgotado"))
    monkeypatch.setattr("integrations.exchange_client.httpx.Client", cliente)

    assert exchange_service.consultar_cotacao("USD") == "A API de câmbio demorou para responder."
