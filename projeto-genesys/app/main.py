# app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path='../.env')

# --- Seção de Carregamento do Modelo (a ser ativada) ---
# Aqui é onde instanciaremos o nosso modelo de linguagem.
# Por enquanto, está comentado para garantir que o servidor suba sem o modelo.

# from langchain_community.llms import LlamaCpp
# from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
# from langchain.chains import ConversationChain
# from langchain.memory import ConversationBufferWindowMemory
# from langchain.prompts import PromptTemplate

# # --- Configuração da Memória (Hipocampo) ---
# # Usaremos uma memória de conversação com janela para manter o contexto recente.
# memory = ConversationBufferWindowMemory(k=5) # Lembra das últimas 5 interações

# # --- Configuração do Modelo ---
# model_name = os.getenv("MODEL_NAME")
# model_quantization = os.getenv("MODEL_QUANTIZATION")
# # O caminho agora aponta para um diretório 'models' na raiz do projeto
# model_path = f"./models/{model_name}.{model_quantization}.gguf"

# # Gerenciador de Callbacks para streaming da resposta no console
# callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# # Carregar o modelo de linguagem
# llm = LlamaCpp(
#     model_path=model_path,
#     n_gpu_layers=-1,
#     n_batch=512,
#     n_ctx=4096, # Aumentando o contexto
#     f16_kv=True,
#     callback_manager=callback_manager,
#     verbose=True,
# )

# # --- Template de Prompt (A Personalidade do Agente) ---
# # Este template guia o comportamento do nosso agente.
# template = """
# Você é o Agente Gênesys, uma IA soberana especializada em programação e assistência de desenvolvimento.
# Sua missão é auxiliar seu criador a construir, analisar e otimizar projetos de software.
# Você é colaborativo, preciso e está sempre aprendendo.
# Lembre-se das interações passadas para manter o contexto.

# Conversa Atual:
# {history}
# Criador: {input}
# Agente Gênesys:
# """

# PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

# # --- A Cadeia de Conversação (O Sistema Nervoso Central) ---
# # Une o prompt, o modelo e a memória.
# conversation = ConversationChain(
#     prompt=PROMPT,
#     llm=llm,
#     verbose=True,
#     memory=memory
# )
# ---------------------------------------------------------

# Instanciar a aplicação FastAPI
app = FastAPI(
    title="Projeto Gênesys",
    description="A infraestrutura para um agente de IA soberano.",
    version="0.1.0",
)

@app.get("/", tags=["Status"])
async def root():
    """
    Endpoint principal para verificar o status da API.
    """
    return {"message": f"Bem-vindo ao projeto-genesys. Servidor operacional. Modelo '{os.getenv('MODEL_NAME')}' aguardando ordens."}

@app.post("/chat", tags=["Interação"])
async def chat_with_agent(prompt: str):
    """
    Endpoint para interagir com o Agente Gênesys.
    """
    # Lógica de resposta do modelo (quando ativado)
    # response = conversation.predict(input=prompt)
    # return {"response": response}
    
    # Resposta placeholder enquanto o modelo não está ativo
    return {"message": "Endpoint de chat está pronto. A lógica do modelo precisa ser ativada.", "received_prompt": prompt}


if __name__ == "__main__":
    import uvicorn
    # Para rodar: uvicorn app.main:app --reload --app-dir .
    uvicorn.run("main:app", host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", 8000)), reload=True)
