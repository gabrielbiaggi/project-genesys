# app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from typing import List, Dict

# Importar a lógica de criação do agente
from app.agent_logic import create_genesis_agent

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path='.env')

# --- Seção de Criação do Agente ---
# Isso agora inicializa o agente completo com ferramentas e memória.
agent_executor = create_genesis_agent()

# ---------------------------------------------------------

# Modelo de dados para a requisição
class ChatRequest(BaseModel):
    prompt: str

# --- Modelos para compatibilidade com a API OpenAI/Cursor ---
class OpenAIMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    temperature: float = 0.7

class OpenAIChatChoice(BaseModel):
    index: int = 0
    message: OpenAIMessage
    finish_reason: str = "stop"

class OpenAIChatResponse(BaseModel):
    id: str = "chatcmpl-genesys"
    object: str = "chat.completion"
    created: int = 0
    model: str
    choices: List[OpenAIChatChoice]

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
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint para interagir com o Agente Gênesys.
    Recebe um prompt e retorna a resposta do agente.
    """
    try:
        # Usamos o agent_executor para invocar o agente com o prompt.
        response = agent_executor.invoke({"input": request.prompt})
        return {"response": response.get("output")}
    except Exception as e:
        # Tratamento de erro para o caso de o modelo falhar ou outro problema ocorrer
        return {"error": f"Ocorreu um erro ao processar sua solicitação: {str(e)}"}

@app.post("/v1/chat/completions", tags=["Compatibilidade Cursor/OpenAI"], response_model=OpenAIChatResponse)
async def openai_compatible_chat(request: OpenAIChatRequest):
    """
    Endpoint compatível com a API da OpenAI para integração com o Cursor.
    """
    # Extrai a última mensagem do usuário para usar como prompt
    user_prompt = ""
    if request.messages:
        user_prompt = request.messages[-1].content
    
    try:
        # Invoca o agente Gênesys
        agent_response = agent_executor.invoke({"input": user_prompt})
        response_text = agent_response.get("output", "Não consegui gerar uma resposta.")

        # Constrói a resposta no formato OpenAI
        response_message = OpenAIMessage(role="assistant", content=response_text)
        choice = OpenAIChatChoice(message=response_message)
        return OpenAIChatResponse(model=request.model, choices=[choice])

    except Exception as e:
        error_message = OpenAIMessage(role="assistant", content=f"Erro no Agente Gênesys: {str(e)}")
        choice = OpenAIChatChoice(message=error_message)
        return OpenAIChatResponse(model=request.model, choices=[choice])


if __name__ == "__main__":
    import uvicorn
    # Para rodar: uvicorn app.main:app --reload
    uvicorn.run("main:app", host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", 8000)), reload=True)
