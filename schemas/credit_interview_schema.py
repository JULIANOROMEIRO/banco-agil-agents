from typing import Literal

from pydantic import BaseModel, Field


class DadosEntrevistaCredito(BaseModel):
    renda_mensal: float | None = Field(
        default=None,
        ge=0,
        description="Renda mensal informada pelo cliente. Nulo se não foi dita.",
    )
    tipo_emprego: Literal["formal", "autonomo", "desempregado"] | None = Field(
        default=None,
        description="formal, autonomo ou desempregado. Use autonomo sem acento. Nulo se não foi dito.",
    )
    despesas: float | None = Field(
        default=None,
        ge=0,
        description="Despesas fixas mensais. Nulo se não foram ditas.",
    )
    dependentes: int | None = Field(
        default=None,
        ge=0,
        description="Número de dependentes. Nulo se não foi dito.",
    )
    tem_dividas: bool | None = Field(
        default=None,
        description="True se há dívidas ativas, False se não há. Nulo se o cliente não respondeu.",
    )
