from crud.arquivos import DataFileError
from crud import crud_clientes

from agents.triage.tools import build_triage_tools


def atender(session, texto: str) -> str:
    autenticar_cliente, finalizar_atendimento = build_triage_tools(session)

    cpf = crud_clientes.extrair_cpf(texto)
    data = crud_clientes.extrair_data(texto)
    if cpf:
        session.cpf = cpf
    if data:
        session.data_nascimento = data

    if not session.cpf:
        return "Para começar, informe o seu CPF."
    if not session.data_nascimento:
        return "Agora informe a data de nascimento no formato DD/MM/AAAA."

    try:
        resultado = autenticar_cliente.invoke(
            {"cpf": session.cpf, "data_nascimento": session.data_nascimento}
        )
        if resultado == "sucesso":
            session.authenticated = True
            session.active_agent = None
            cliente = crud_clientes.buscar_cliente(session.cpf)
            nome = cliente.nome if cliente else "cliente"
            return f"Autenticação concluída, {nome}. Como posso ajudar?"
    except DataFileError as exc:
        return str(exc)

    session.cpf = None
    session.data_nascimento = None
    session.auth_attempts += 1
    if session.auth_attempts >= 3:
        finalizar_atendimento.invoke({})
        return "Não foi possível autenticar após 3 tentativas. Atendimento encerrado."
    return f"Dados não conferem. Tentativa {session.auth_attempts} de 3. Informe CPF e data de nascimento."
