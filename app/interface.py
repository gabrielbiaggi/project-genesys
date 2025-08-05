# app/interface.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente para obter a URL da API
load_dotenv(dotenv_path='../.env')
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))

# URL do endpoint de chat do seu Agente Gênesys
CHAT_API_URL = f"http://{API_HOST}:{API_PORT}/chat"

# --- Configuração da Página Streamlit ---
st.set_page_config(
    page_title="Interface do Agente Gênesys",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Agente Gênesys")
st.caption("Sua IA soberana para desenvolvimento de software.")

# --- Gerenciamento do Histórico da Conversa ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Entrada do Usuário ---
if prompt := st.chat_input("Qual é a sua diretiva?"):
    # Adicionar mensagem do usuário ao histórico e exibi-la
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamar a API do Gênesys e exibir a resposta
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Preparar os dados para a requisição POST
            payload = {"prompt": prompt}
            
            # Enviar a requisição para a API
            response = requests.post(CHAT_API_URL, json=payload)
            response.raise_for_status() # Lança um erro para status HTTP 4xx/5xx
            
            api_response = response.json()

            if "response" in api_response:
                full_response = api_response["response"]
            elif "error" in api_response:
                full_response = f"Erro no Agente: {api_response['error']}"
            else:
                full_response = "Resposta inesperada da API."

        except requests.exceptions.RequestException as e:
            full_response = f"Erro ao conectar-se com a API do Gênesys: {e}"
        except Exception as e:
            full_response = f"Ocorreu um erro inesperado: {e}"

        message_placeholder.markdown(full_response)

    # Adicionar resposta do assistente ao histórico
    st.session_state.messages.append({"role": "assistant", "content": full_response})
