"""Leitura e gravação dos CSV. Erros de arquivo ficam nesta camada."""

import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MENSAGEM_DADOS = (
    "Não foi possível consultar os dados neste momento. "
    "Tente novamente mais tarde."
)


class DataFileError(RuntimeError):
    pass


def _falhar(caminho: Path, exc: Exception) -> None:
    logger.exception("Falha ao acessar %s", caminho)
    raise DataFileError(MENSAGEM_DADOS) from exc


def ler_dicts(caminho: Path) -> list[dict[str, str]]:
    try:
        with caminho.open(encoding="utf-8", newline="") as arquivo:
            return list(csv.DictReader(arquivo))
    except (FileNotFoundError, PermissionError, OSError, csv.Error) as exc:
        _falhar(caminho, exc)


def ler_se_existir(caminho: Path) -> list[dict[str, str]]:
    try:
        if not caminho.exists() or caminho.stat().st_size == 0:
            return []
    except (FileNotFoundError, PermissionError, OSError) as exc:
        _falhar(caminho, exc)
    return ler_dicts(caminho)


def gravar_dicts(caminho: Path, campos: list[str], linhas: list[dict]) -> None:
    try:
        with caminho.open("w", encoding="utf-8", newline="") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=campos)
            writer.writeheader()
            writer.writerows(linhas)
    except (FileNotFoundError, PermissionError, OSError, csv.Error) as exc:
        _falhar(caminho, exc)


def anexar_dict(caminho: Path, campos: list[str], linha: dict) -> None:
    try:
        novo = not caminho.exists() or caminho.stat().st_size == 0
        with caminho.open("a", encoding="utf-8", newline="") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=campos)
            if novo:
                writer.writeheader()
            writer.writerow(linha)
    except (FileNotFoundError, PermissionError, OSError, csv.Error) as exc:
        _falhar(caminho, exc)
