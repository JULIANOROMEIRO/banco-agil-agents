from pathlib import Path

from core.config import settings
from crud.arquivos import ler_dicts
from schemas.cliente_schema import ScoreFaixa


def _caminho() -> Path:
    return Path(settings.DATA_DIR) / "score_limite.csv"


def buscar_faixa_score(score: int) -> ScoreFaixa | None:
    for linha in ler_dicts(_caminho()):
        faixa = ScoreFaixa(
            score_min=int(linha["score_min"]),
            score_max=int(linha["score_max"]),
            limite_maximo=float(linha["limite_maximo"]),
        )
        if faixa.score_min <= score <= faixa.score_max:
            return faixa
    return None
