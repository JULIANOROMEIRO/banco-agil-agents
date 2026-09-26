import re

_PADROES_ENCERRAMENTO = (
    r"\bquero encerrar\b",
    r"\bencerrar (?:o )?atendimento\b",
    r"\bquero finalizar\b",
    r"\bfinalizar (?:o |meu )?atendimento\b",
    r"\bpode finalizar\b",
    r"\bquero sair\b",
    r"\bquero terminar\b",
    r"\bterminar (?:o |meu )?atendimento\b",
    r"\btchau\b",
)

_PADRAO_ENCERRAMENTO = re.compile("|".join(_PADROES_ENCERRAMENTO), re.IGNORECASE)


def quer_encerrar(texto: str) -> bool:
    return bool(_PADRAO_ENCERRAMENTO.search((texto or "").strip()))
