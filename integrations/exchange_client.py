"""Integração HTTP com a API pública de câmbio."""

import re

import httpx

from core.config import settings


class ExchangeError(Exception):
    def __init__(self, mensagem: str):
        self.mensagem = mensagem
        super().__init__(mensagem)


def consultar_cotacao(moeda: str) -> dict:
    codigo = (moeda or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", codigo):
        raise ExchangeError("Moeda inválida. Use o código de 3 letras, por exemplo USD.")
    if codigo == "BRL":
        return {"moeda": "BRL", "cotacao_brl": 1.0, "data": None}

    url = f"{settings.EXCHANGE_API_URL.rstrip('/')}/latest"
    try:
        with httpx.Client(timeout=settings.EXCHANGE_TIMEOUT_SECONDS) as client:
            response = client.get(url, params={"from": codigo, "to": "BRL"})
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise ExchangeError("A API de câmbio demorou para responder.") from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise ExchangeError("Moeda inválida.") from exc
        raise ExchangeError("A API de câmbio está indisponível.") from exc
    except httpx.HTTPError as exc:
        raise ExchangeError("A API de câmbio está indisponível.") from exc

    try:
        payload = response.json()
        cotacao = float(payload["rates"]["BRL"])
    except (ValueError, KeyError, TypeError) as exc:
        raise ExchangeError("A API de câmbio retornou um payload inesperado.") from exc

    return {"moeda": codigo, "cotacao_brl": cotacao, "data": payload.get("date")}
