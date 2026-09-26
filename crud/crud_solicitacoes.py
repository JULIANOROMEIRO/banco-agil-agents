from pathlib import Path

from core.config import settings
from crud.arquivos import anexar_dict, ler_se_existir
from schemas.cliente_schema import SolicitacaoLimite

CAMPOS = [
    "cpf_cliente",
    "data_hora_solicitacao",
    "limite_atual",
    "novo_limite_solicitado",
    "status_pedido",
]


def _caminho() -> Path:
    return Path(settings.DATA_DIR) / "solicitacoes_aumento_limite.csv"


def salvar_solicitacao(solicitacao: SolicitacaoLimite) -> SolicitacaoLimite:
    anexar_dict(_caminho(), CAMPOS, solicitacao.model_dump())
    return solicitacao


def listar_solicitacoes() -> list[SolicitacaoLimite]:
    return [
        SolicitacaoLimite(
            cpf_cliente=linha["cpf_cliente"],
            data_hora_solicitacao=linha["data_hora_solicitacao"],
            limite_atual=float(linha["limite_atual"]),
            novo_limite_solicitado=float(linha["novo_limite_solicitado"]),
            status_pedido=linha["status_pedido"],
        )
        for linha in ler_se_existir(_caminho())
    ]
