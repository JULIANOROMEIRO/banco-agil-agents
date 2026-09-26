"""Interface do Banco Ágil. Conversa com a API por HTTP."""

import os

import httpx
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="Banco Ágil", page_icon="💬")
st.title("Banco Ágil")
st.caption("Atendimento com agentes. Todos os dados exibidos são sintéticos.")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "history" not in st.session_state:
    st.session_state.history = []
if "finished" not in st.session_state:
    st.session_state.finished = False


def _url(caminho: str) -> str:
    return f"{API_BASE_URL}/api/v1{caminho}"


def iniciar() -> None:
    try:
        response = httpx.post(_url("/sessions"), timeout=30)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        st.error(f"Não foi possível iniciar o atendimento: {exc}")
        return
    dados = response.json()
    st.session_state.session_id = dados["session_id"]
    st.session_state.history = dados["history"]
    st.session_state.finished = dados["finished"]


def enviar(texto: str) -> None:
    try:
        response = httpx.post(
            _url(f"/sessions/{st.session_state.session_id}/messages"),
            json={"message": texto},
            timeout=120,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detalhe = exc.response.json().get("detail", exc.response.text)
        st.error(detalhe)
        return
    except httpx.HTTPError as exc:
        st.error(f"Falha ao enviar a mensagem: {exc}")
        return
    dados = response.json()
    st.session_state.history = dados["session"]["history"]
    st.session_state.finished = dados["session"]["finished"]


def encerrar() -> None:
    if st.session_state.session_id and not st.session_state.finished:
        enviar("quero encerrar")
    st.session_state.session_id = None
    st.session_state.history = []
    st.session_state.finished = False
    st.rerun()


col_iniciar, col_encerrar = st.columns(2)
with col_iniciar:
    if st.button("Iniciar atendimento", disabled=st.session_state.session_id is not None):
        iniciar()
with col_encerrar:
    if st.button("Encerrar conversa", disabled=st.session_state.session_id is None):
        encerrar()

if st.session_state.session_id:
    st.text(f"Sessão: {st.session_state.session_id}")

def _texto_visivel(texto: str) -> str:
    return (
        texto.replace("\\", "\\\\")
        .replace("$", r"\$")
        .replace("*", r"\*")
        .replace("_", r"\_")
    )


for item in st.session_state.history:
    papel = "assistant" if item["role"] == "assistant" else "user"
    with st.chat_message(papel):
        st.markdown(_texto_visivel(item["content"]))

if st.session_state.session_id and not st.session_state.finished:
    mensagem = st.chat_input("Escreva sua mensagem")
    if mensagem:
        enviar(mensagem)
        st.rerun()
