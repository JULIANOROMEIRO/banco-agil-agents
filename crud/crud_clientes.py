import re
from pathlib import Path

from core.config import settings
from crud.arquivos import gravar_dicts, ler_dicts
from schemas.cliente_schema import Cliente

CAMPOS = ["cpf", "data_nascimento", "nome", "limite_atual", "score"]


def somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def normalizar_data(valor: str) -> str | None:
    texto = (valor or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        return texto
    match = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if match:
        dia, mes, ano = match.groups()
        return f"{ano}-{mes}-{dia}"
    return None


def extrair_cpf(texto: str) -> str | None:
    match = re.search(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", texto or "")
    if not match:
        return None
    digitos = somente_digitos(match.group())
    if len(digitos) != 11:
        return None
    return digitos


def extrair_data(texto: str) -> str | None:
    match = re.search(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", texto or "")
    if not match:
        return None
    return normalizar_data(match.group())


def _caminho() -> Path:
    return Path(settings.DATA_DIR) / "clientes.csv"


def _ler() -> list[dict[str, str]]:
    return ler_dicts(_caminho())


def _gravar(linhas: list[dict[str, str]]) -> None:
    gravar_dicts(_caminho(), CAMPOS, linhas)


def _para_cliente(linha: dict[str, str]) -> Cliente:
    return Cliente(
        cpf=linha["cpf"],
        data_nascimento=linha["data_nascimento"],
        nome=linha["nome"],
        limite_atual=float(linha["limite_atual"]),
        score=int(linha["score"]),
    )


def buscar_cliente(cpf: str) -> Cliente | None:
    cpf_normalizado = somente_digitos(cpf)
    for linha in _ler():
        if linha["cpf"] == cpf_normalizado:
            return _para_cliente(linha)
    return None


def autenticar_cliente(cpf: str, data_nascimento: str) -> Cliente | None:
    cliente = buscar_cliente(cpf)
    data_normalizada = normalizar_data(data_nascimento)
    if cliente is None or data_normalizada is None:
        return None
    if cliente.data_nascimento != data_normalizada:
        return None
    return cliente


def consultar_limite(cpf: str) -> float | None:
    cliente = buscar_cliente(cpf)
    if cliente is None:
        return None
    return cliente.limite_atual


def atualizar_score(cpf: str, score: int) -> Cliente | None:
    cpf_normalizado = somente_digitos(cpf)
    linhas = _ler()
    atualizado = None
    for linha in linhas:
        if linha["cpf"] == cpf_normalizado:
            linha["score"] = str(score)
            atualizado = linha
            break
    if atualizado is None:
        return None
    _gravar(linhas)
    return _para_cliente(atualizado)


def atualizar_limite(cpf: str, limite: float) -> Cliente | None:
    cpf_normalizado = somente_digitos(cpf)
    linhas = _ler()
    atualizado = None
    for linha in linhas:
        if linha["cpf"] == cpf_normalizado:
            linha["limite_atual"] = f"{limite:.2f}"
            atualizado = linha
            break
    if atualizado is None:
        return None
    _gravar(linhas)
    return _para_cliente(atualizado)
