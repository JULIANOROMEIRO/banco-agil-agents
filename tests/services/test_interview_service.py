import pytest
from pydantic import ValidationError

from schemas.credit_interview_schema import DadosEntrevistaCredito
from services import interview_service


def test_calculo_do_score():
    score = interview_service.calcular_score(
        renda_mensal=8000,
        tipo_emprego="formal",
        despesas=2000,
        dependentes=1,
        tem_dividas=False,
    )

    assert score == 600


def test_score_entre_0_e_1000():
    baixo = interview_service.calcular_score(0, "desempregado", 0, 10, True)
    alto = interview_service.calcular_score(100000, "formal", 0, 0, False)

    assert baixo == 0
    assert alto == 1000


def test_valor_negativo_e_rejeitado():
    with pytest.raises(ValidationError):
        DadosEntrevistaCredito(renda_mensal=-1)

    with pytest.raises(ValueError):
        interview_service.calcular_score(-1, "formal", 0, 0, False)
