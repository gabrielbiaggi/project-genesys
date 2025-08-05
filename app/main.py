# app/main.py
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel
from typing import List
import pywinpty
import asyncio
import shutil

# Importar a lógica de criação do agente e ferramentas
from app.agent_logic import create_genesys_agent
from app.tools.file_system_tool import SAFE_WORKSPACE, list_files, read_file, propose_file_change, apply_file_change

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path='.env')

# --- Seção de Criação do Agente ---
agent_executor = create_genesys_agent()

# --- Configuração do Logging de Interações para Fine-Tuning ---
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
INTERACTION_LOG_FILE = os.path.join(LOGS_DIR, 'interaction_logs.jsonl')

def log_interaction(prompt: str, response: dict):
    """Salva a interação completa (prompt, resposta, passos) no arquivo de log."""
    with open(INTERACTION_LOG_FILE, 'a', encoding='utf-8') as f:
        # Prepara os intermediate_steps para serialização, convertendo objetos
        serializable_steps = []
        if "intermediate_steps" in response:
            for step in response["intermediate_steps"]:
                # step é uma tupla (AgentAction, observation)
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
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\\n')

# --- Modelos de Dados Pydantic ---
class ChatRequest(BaseModel):
    prompt: str

class FilePathRequest(BaseModel):
    path: str

class FileWriteRequest(BaseModel):
    path: str
    content: str

# Instanciar a aplicação FastAPI
app = FastAPI(
    title="Projeto Gênesys",
    description="A infraestrutura para um agente de IA soberano, com uma IDE web integrada.",
    version="0.2.0",
)

# --- Configuração do CORS ---
# Permite que o frontend (rodando em outra porta) se comunique com a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, restrinja para o domínio do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints da API ---

@app.get("/", tags=["Status"])
async def root():
    """Endpoint principal para verificar o status da API."""
    return {"message": f"Bem-vindo ao projeto-genesys. Servidor operacional. Modelo '{os.getenv('MODEL_GGUF_FILENAME')}' aguardando ordens."}

@app.post("/chat", tags=["Interação com Agente"])
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint para interagir com o Agente Gênesys.
    Recebe um prompt, retorna a resposta do agente e loga a interação.
    """
    try:
        response = agent_executor.invoke({"input": request.prompt})
        
        # Loga a interação completa para futuro fine-tuning
        log_interaction(request.prompt, response)

        # Prepara os intermediate_steps para serem enviados como JSON
        serializable_steps = []
        if "intermediate_steps" in response:
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
        return JSONResponse(status_code=500, content={"error": f"Ocorreu um erro ao processar sua solicitação: {str(e)}"})

# --- Endpoints para Gerenciamento de Arquivos da IDE ---

@app.get("/files/list", tags=["Gerenciamento de Arquivos"])
async def get_file_list():
    """Lista todos os arquivos e diretórios no workspace seguro."""
    return {"files": list_files("")}

@app.get("/files/read", tags=["Gerenciamento de Arquivos"])
async def read_file_content(path: str):
    """Lê o conteúdo de um arquivo específico no workspace."""
    content = read_file(path)
    if content.startswith("Erro:"):
        return JSONResponse(status_code=404, content={"detail": content})
    return {"content": content}

@app.post("/files/write", tags=["Gerenciamento de Arquivos"])
async def write_file_content(request: FileWriteRequest):
    """
    Escreve (aplica) o conteúdo em um arquivo. 
    Este endpoint chama a ferramenta 'apply_file_change' que efetivamente escreve no disco.
    """
    result = apply_file_change(request.path, request.content)
    if result.startswith("Erro:"):
        return JSONResponse(status_code=400, content={"detail": result})
    return {"message": result}

@app.post("/files/upload", tags=["Gerenciamento de Arquivos"])
async def upload_file(file: UploadFile = File(...)):
    """
    Faz o upload de um arquivo para o diretório raiz do workspace seguro.
    Se um arquivo com o mesmo nome existir, ele será sobrescrito.
    """
    try:
        # Caminho seguro para salvar o arquivo
        file_path = os.path.join(SAFE_WORKSPACE, file.filename)
        
        # Validação para garantir que o caminho final ainda está dentro do SAFE_WORKSPACE
        if not os.path.abspath(file_path).startswith(os.path.abspath(SAFE_WORKSPACE)):
            return JSONResponse(status_code=400, content={"detail": "Nome de arquivo inválido."})

        # Escreve o arquivo no disco
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"filename": file.filename, "message": "Arquivo enviado com sucesso."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Não foi possível fazer o upload do arquivo: {e}"})
    finally:
        await file.close()

# --- Endpoint do Terminal via WebSocket ---

@app.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    """Endpoint WebSocket para o terminal interativo."""
    await websocket.accept()
    
    # Inicia um processo de shell (PowerShell no Windows)
    # pywinpty é usado para criar um pseudo-terminal no Windows
    try:
        shell_process = pywinpty.PtyProcess.spawn(
            ['powershell.exe'],
            cwd=SAFE_WORKSPACE,
            env=os.environ.copy()
        )

        async def read_from_shell():
            """Lê a saída do shell e envia para o frontend."""
            while shell_process.isalive():
                try:
                    output = shell_process.read(1024, timeout=0.01)
                    if output:
                        await websocket.send_text(output)
                except pywinpty.errors.PtyProcessError:
                    break # Processo provavelmente terminou
                await asyncio.sleep(0.01) # Evita busy-waiting

        # Cria uma task para ler a saída do shell continuamente
        read_task = asyncio.create_task(read_from_shell())

        try:
            while True:
                # Recebe dados do frontend (terminal web)
                data = await websocket.receive_text()
                shell_process.write(data)
        except WebSocketDisconnect:
            print("Cliente desconectado do terminal.")
        finally:
            read_task.cancel() # Para a task de leitura
            if shell_process.isalive():
                shell_process.close() # Encerra o processo do shell

    except Exception as e:
        error_message = f"Erro ao iniciar o terminal: {e}"
        print(error_message)
        await websocket.send_text(f"\\r\\n{error_message}\\r\\n")
    finally:
        await websocket.close()
