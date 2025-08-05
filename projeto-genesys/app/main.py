# app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Instanciar a aplicação FastAPI
app = FastAPI(
    title="Projeto Gênesis",
    description="A infraestrutura para um agente de IA soberano.",
    version="0.1.0",
)

# --- Seção de Carregamento do Modelo (a ser ativada) ---
# Aqui é onde instanciaremos o nosso modelo de linguagem.
# Por enquanto, está comentado para garantir que o servidor suba sem o modelo.

# from langchain_community.llms import LlamaCpp
# from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler

# model_name = os.getenv("MODEL_NAME")
# model_quantization = os.getenv("MODEL_QUANTIZATION")
# model_path = f"../models/{model_name}.{model_quantization}.gguf"

# # Gerenciador de Callbacks para streaming da resposta
# callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# # Carregar o modelo
# llm = LlamaCpp(
#     model_path=model_path,
#     n_gpu_layers=-1,  # Carregar todas as camadas na GPU
#     n_batch=512,
#     n_ctx=2048,
#     f16_kv=True,  # Deve ser True para GPUs modernas
#     callback_manager=callback_manager,
#     verbose=True,
# )

# ---------------------------------------------------------

@app.get("/", tags=["Status"])
async def root():
    """
    Endpoint principal para verificar o status da API.
    """
    return {"message": f"Bem-vindo ao Projeto Gênesis. Servidor operacional. Modelo '{os.getenv('MODEL_NAME')}' aguardando ordens."}

@app.post("/chat", tags=["Interação"])
async def chat_with_agent(prompt: str):
    """
    Endpoint para interagir com o Agente Gênesis.
    (Lógica a ser implementada)
    """
    # Lógica de resposta do modelo
    # response = llm.invoke(prompt)
    # return {"response": response}
    return {"message": "Endpoint de chat está pronto. A lógica do modelo precisa ser ativada."}


if __name__ == "__main__":
    import uvicorn
    # Para rodar: uvicorn app.main:app --reload
    uvicorn.run(app, host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", 8000)))
