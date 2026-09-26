from langchain_core.tools import tool

from crud import crud_clientes


def build_triage_tools(session):
    @tool
    def autenticar_cliente(cpf: str, data_nascimento: str) -> str:
        """Confere CPF e data de nascimento no cadastro de clientes."""
        cliente = crud_clientes.autenticar_cliente(cpf, data_nascimento)
        if cliente is None:
            return "falha"
        session.cpf = cliente.cpf
        session.data_nascimento = cliente.data_nascimento
        return "sucesso"

    @tool
    def finalizar_atendimento() -> str:
        """Encerra o atendimento atual."""
        session.finished = True
        return "Atendimento encerrado."

    return autenticar_cliente, finalizar_atendimento
