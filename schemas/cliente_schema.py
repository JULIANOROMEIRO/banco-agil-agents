from pydantic import BaseModel, Field


class Cliente(BaseModel):
    cpf: str
    data_nascimento: str
    nome: str
    limite_atual: float
    score: int


class ScoreFaixa(BaseModel):
    score_min: int
    score_max: int
    limite_maximo: float


class SolicitacaoLimite(BaseModel):
    cpf_cliente: str
    data_hora_solicitacao: str
    limite_atual: float
    novo_limite_solicitado: float
    status_pedido: str


class LimiteConsulta(BaseModel):
    nome: str
    cpf: str
    limite_atual: float
    score: int
    mensagem: str


class SolicitacaoResultado(BaseModel):
    status_pedido: str
    limite_atual: float
    novo_limite_solicitado: float
    limite_maximo: float
    mensagem: str
