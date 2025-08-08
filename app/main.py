# app/main.py
import sys
import os

# --- Correção Crítica para o PYTHONPATH ---
# Adiciona o diretório raiz do projeto ao sys.path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- Fim da Correção ---

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import json
from pydantic import BaseModel
from typing import Optional
import base64

from app.tools.download_tool import download_model_tool
from app.tools.script_execution_tool import execute_python_script

# --- Carregamento Condicional do Agente ---
agent_executor = None
multimodal_chat_handler = None
create_multimodal_message = None

# Tenta carregar o agente de IA. Se falhar, o servidor continuará em modo de gerenciamento.
try:
    from app.agent_logic import create_genesys_agent, create_multimodal_message
    agent_executor, multimodal_chat_handler = create_genesys_agent()
    print("INFO: Agente Genesys e ferramentas carregados com sucesso.")
except Exception as e:
    print(f"AVISO: Falha ao carregar o agente de IA: {e}")
    print("AVISO: O servidor continuará em modo de gerenciamento sem a capacidade de chat.")
    agent_executor = None
    multimodal_chat_handler = None

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path='.env')

# --- Configuração do Logging de Interações para Fine-Tuning ---
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
INTERACTION_LOG_FILE = os.path.join(LOGS_DIR, 'interaction_logs.jsonl')

def log_interaction(prompt: str, response: dict):
    """Salva a interação completa (prompt, resposta, passos) no arquivo de log."""
    with open(INTERACTION_LOG_FILE, 'a', encoding='utf-8') as f:
        serializable_steps = []
        if "intermediate_steps" in response and response["intermediate_steps"] is not None:
            for step in response["intermediate_steps"]:
                action, observation = step
                serializable_steps.append({
                    "tool": action.tool,
                    "tool_input": action.tool_input,
                    "observation": observation,
                    "log": action.log 
                })

        log_entry = {
            "prompt": prompt,
            "final_answer": response.get("output", ""),
            "intermediate_steps": serializable_steps
        }
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

# --- Modelos de Dados Pydantic ---
class ChatRequest(BaseModel):
    prompt: str
    image: str | None = None # Imagem opcional, em base64

class ScriptExecutionRequest(BaseModel):
    script_path: str

# Instanciar a aplicação FastAPI
app = FastAPI(
    title="API do Agente Genesys",
    description="Uma API minimalista para servir um agente de IA soberano para orquestradores como o AutoGen.",
    version="1.0.0",
)

@app.on_event("startup")
async def on_startup():
    """
    Evento de inicialização para acionar tarefas em segundo plano, como o download do modelo.
    """
    print("INFO: Servidor iniciando. Verificando a existência dos modelos...")
    # Em um cenário de produção real, isso seria melhor tratado com BackgroundTasks
    # para não bloquear a inicialização, mas para o setup inicial, é suficiente.
    try:
        result = download_model_tool.invoke({})
        print(f"INFO: Verificação de download do modelo concluída. Detalhes: {result}")
    except Exception as e:
        print(f"ERRO: Falha ao executar a ferramenta de download na inicialização: {e}")

# --- Endpoints da API ---

@app.get("/", tags=["Status"])
async def root():
    """Endpoint principal para verificar o status da API."""
    agent_status = "operacional" if agent_executor else "não carregado"
    return {"message": f"Bem-vindo à API do Genesys. Servidor operacional. Agente: {agent_status}. Modelo: '{os.getenv('MODEL_GGUF_FILENAME')}'."}

@app.post("/chat", tags=["Interação com Agente"])
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint principal para interagir com o Agente Genesys.
    Recebe um prompt e, opcionalmente, uma imagem em base64.
    Retorna a resposta do agente e loga a interação para fine-tuning.
    """
    if not agent_executor:
        return JSONResponse(
            status_code=503, # Service Unavailable
            content={"error": "O Agente de IA não está disponível. O servidor pode estar em modo de desenvolvimento ou falhou ao carregar o modelo."}
        )
        
    try:
        # --- Lógica de Roteamento: Multimodal vs. Ferramentas ---
        if request.image and multimodal_chat_handler and create_multimodal_message:
            # Rota Multimodal: Lida com texto e imagem
            print("INFO: Executando rota de chat multimodal (LLaVA)...")
            image_bytes = base64.b64decode(request.image)
            message = create_multimodal_message(request.prompt, image_bytes)
            
            # Invoca o handler LLaVA
            result = multimodal_chat_handler.invoke(message)
            
            # Log simples para a interação multimodal
            log_interaction(request.prompt, {"output": result, "intermediate_steps": []})
            
            return {"response": result, "intermediate_steps": []}

        else:
            # Rota Padrão: Agente com ferramentas (ReAct)
            print("INFO: Executando rota de agente com ferramentas (ReAct)...")
            response = agent_executor.invoke({"input": request.prompt})
            
            # Loga a interação completa para futuro fine-tuning
            log_interaction(request.prompt, response)

            # Prepara os intermediate_steps para serem enviados como JSON
            serializable_steps = []
            if "intermediate_steps" in response and response["intermediate_steps"] is not None:
                for step in response["intermediate_steps"]:
                    action, observation = step
                    serializable_steps.append({
                        "tool": action.tool,
                        "tool_input": action.tool_input,
                        "log": action.log,
                        "observation": observation
                    })
            
            return {
                "response": response.get("output", "O agente não forneceu uma saída."),
                "intermediate_steps": serializable_steps
            }
    except Exception as e:
        print(f"ERRO: Ocorreu um erro ao processar a solicitação: {e}")
        return JSONResponse(status_code=500, content={"error": f"Ocorreu um erro interno no servidor: {str(e)}"})

@app.post("/download-model", tags=["Gerenciamento de Modelo"])
async def download_model_endpoint():
    """
    Endpoint para acionar o download do modelo de IA e do projetor multimodal.
    A execução é feita em background para não bloquear a API.
    """
    try:
        # A ferramenta é síncrona, mas a chamamos de um endpoint assíncrono.
        # Para um download longo, o ideal seria rodar em um processo separado (ex: com Celery ou BackgroundTasks do FastAPI).
        # Para simplificar, faremos a chamada direta, mas cientes de que pode bloquear por um tempo.
        result = download_model_tool.invoke({})
        return {"status": "Download iniciado/verificado.", "details": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Falha ao acionar a ferramenta de download: {str(e)}"})

@app.post("/run-script", tags=["Execução de Scripts"])
async def run_script_endpoint(request: ScriptExecutionRequest):
    """
    Endpoint para executar um script Python especificado dentro do ambiente do servidor.
    """
    try:
        result = execute_python_script.invoke({"script_path": request.script_path})
        return {"status": "Execução do script solicitada.", "details": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Falha ao acionar a ferramenta de execução de script: {str(e)}"})
