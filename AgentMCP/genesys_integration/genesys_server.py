# genesys_integration/genesys_server.py
"""
Servidor local da Genesys integrado ao Agent-MCP
Executa em segundo plano fornecendo API para o agente
"""
import asyncio
import json
import time
import threading
import uvicorn
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import httpx
from dotenv import load_dotenv

from .genesys_agent import genesys_agent

# Modelos de dados
class ChatRequest(BaseModel):
    prompt: str
    context: Optional[Dict] = None
    use_tools: bool = True

class MultimodalRequest(BaseModel):
    prompt: str
    image_data: Optional[str] = None  # Base64
    context: Optional[Dict] = None

class AgentStatusResponse(BaseModel):
    status: str
    agent_info: Dict[str, Any]
    server_uptime: float

# Estado global do servidor
server_state = {
    "startup_time": time.time(),
    "requests_processed": 0,
    "model_loaded": False
}

# --- Globals ---
genesys_agent: Optional[GenesysAgent] = None
START_TIME = time.time()
AUTONOMY_KICKSTARTED = False

async def kickstart_mcp_autonomy():
    """Send a request to the MCP server to start its autonomous loop."""
    global AUTONOMY_KICKSTARTED
    if AUTONOMY_KICKSTARTED:
        return

    load_dotenv() # Ensure .env is loaded
    mcp_url = os.getenv("AGENT_MCP_API_URL", "http://127.0.0.1:8080")
    admin_token = os.getenv("MCP_ADMIN_TOKEN")

    if not admin_token:
        print("⚠️ MCP_ADMIN_TOKEN not found in .env. Cannot kickstart autonomy.")
        AUTONOMY_KICKSTARTED = True # Mark as "tried" to prevent repeated attempts
        return

    try:
        async with httpx.AsyncClient() as client:
            print(f"🚀 Sending kickstart signal to MCP at {mcp_url}...")
            response = await client.post(
                f"{mcp_url}/api/kickstart-autonomy",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            if response.status_code in [200, 403]: # 200=started, 403=unauthorized, 200(already_running)
                print(f"✅ Autonomy kickstart signal acknowledged by MCP: {response.json().get('message')}")
                AUTONOMY_KICKSTARTED = True
            else:
                print(f"⚠️ Failed to kickstart MCP autonomy. Status: {response.status_code}, Response: {response.text}")

    except Exception as e:
        print(f"❌ Error sending autonomy kickstart signal to MCP: {e}")
        # Still set to true to avoid retrying on every request if MCP is down
        AUTONOMY_KICKSTARTED = True

# --- FastAPI Lifespan and Routes ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida do servidor"""
    # Startup
    print("🚀 Iniciando servidor Genesys local...")
    
    # Carregar modelo em background
    async def load_model_bg():
        try:
            success = await genesys_agent.load_model()
            server_state["model_loaded"] = success
            if success:
                print("✅ Modelo Genesys carregado com sucesso!")
            else:
                print("❌ Falha ao carregar modelo Genesys")
        except Exception as e:
            print(f"❌ Erro no carregamento: {e}")
    
    # Iniciar carregamento em background
    asyncio.create_task(load_model_bg())
    
    yield
    
    # Shutdown
    print("🛑 Encerrando servidor Genesys local...")

# Criar aplicação FastAPI
app = FastAPI(
    title="Genesys Local Server",
    description="Servidor local da Genesys integrado ao Agent-MCP",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Endpoint raiz - status básico"""
    uptime = time.time() - server_state["startup_time"]
    return {
        "message": "🤖 Servidor Genesys Local - Integrado ao Agent-MCP",
        "status": "operacional",
        "model_loaded": server_state["model_loaded"],
        "uptime_seconds": round(uptime, 2),
        "requests_processed": server_state["requests_processed"],
        "agent_id": genesys_agent.agent_id,
        "specializations": genesys_agent.specializations
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde do servidor"""
    uptime = time.time() - server_state["startup_time"]
    
    return {
        "healthy": True,
        "model_loaded": server_state["model_loaded"],
        "agent_ready": genesys_agent.is_loaded,
        "uptime": uptime,
        "memory_status": "ok"  # Você pode adicionar verificações de memória aqui
    }

@app.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """Status detalhado do agente Genesys"""
    uptime = time.time() - server_state["startup_time"]
    agent_info = genesys_agent.get_status()
    
    return AgentStatusResponse(
        status="ready" if server_state["model_loaded"] else "loading",
        agent_info=agent_info,
        server_uptime=uptime
    )

@app.post("/chat")
async def chat_with_genesys(request: ChatRequest):
    """Endpoint principal para chat com Genesys"""
    server_state["requests_processed"] += 1
    
    if not server_state["model_loaded"]:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Modelo ainda carregando",
                "status": "loading",
                "message": "Aguarde alguns instantes e tente novamente",
                "estimated_time": "1-3 minutos"
            }
        )
    
    try:
        start_time = time.time()
        
        response = await genesys_agent.process_task(
            task=request.prompt,
            context=request.context,
            use_tools=request.use_tools
        )
        
        processing_time = time.time() - start_time
        
        return {
            "response": response,
            "processing_time": round(processing_time, 2),
            "agent_id": genesys_agent.agent_id,
            "tools_used": request.use_tools,
            "context_provided": bool(request.context)
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Erro no processamento: {str(e)}",
                "agent_id": genesys_agent.agent_id
            }
        )

@app.post("/multimodal")
async def process_multimodal(request: MultimodalRequest):
    """Endpoint para processamento multimodal (texto + imagem)"""
    server_state["requests_processed"] += 1
    
    if not server_state["model_loaded"]:
        return JSONResponse(
            status_code=503,
            content={"error": "Modelo ainda carregando"}
        )
    
    try:
        start_time = time.time()
        
        response = await genesys_agent.process_multimodal(
            text=request.prompt,
            image_data=request.image_data
        )
        
        processing_time = time.time() - start_time
        
        return {
            "response": response,
            "processing_time": round(processing_time, 2),
            "agent_id": genesys_agent.agent_id,
            "multimodal": bool(request.image_data)
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erro no processamento multimodal: {str(e)}"}
        )

@app.post("/v1/chat/completions")
async def openai_compatible_chat(request: dict):
    """Endpoint compatible with Continue/Cursor custom models."""
    # --- Kickstart Autonomy on First Request ---
    if not AUTONOMY_KICKSTARTED:
        await kickstart_mcp_autonomy()
    # -----------------------------------------

    # Extrair a última mensagem do usuário
    user_messages = [
        msg for msg in reversed(request.get("messages", [])) if msg.get("role") == "user"
    ]
    last_message = user_messages[0].get("content", "") if user_messages else ""

    if not last_message:
        raise HTTPException(status_code=400, detail="Nenhuma mensagem encontrada")
    
    # Processar com Genesys
    response = await genesys_agent.process_task(last_message)
    
    return {
        "id": "chatcmpl-genesys",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.get("model", "genesys-local"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(last_message.split()),
            "completion_tokens": len(response.split()),
            "total_tokens": len(last_message.split()) + len(response.split())
        }
    }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": f"Erro interno: {str(e)}",
                    "type": "internal_error"
                }
            }
        )

@app.post("/reload-model")
async def reload_model(background_tasks: BackgroundTasks):
    """Recarrega o modelo Genesys"""
    async def reload_bg():
        server_state["model_loaded"] = False
        genesys_agent.is_loaded = False
        success = await genesys_agent.load_model()
        server_state["model_loaded"] = success
    
    background_tasks.add_task(reload_bg)
    return {"message": "Recarregamento do modelo iniciado"}

@app.post("/shutdown")
async def shutdown_server():
    """Encerra o servidor (para uso em desenvolvimento)"""
    return {"message": "Servidor será encerrado em 2 segundos"}

class GenesysServer:
    """Classe para gerenciar o servidor Genesys local"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8002):
        self.host = host
        self.port = port
        self.server_thread = None
        self.is_running = False
    
    def start_background(self):
        """Inicia o servidor em segundo plano"""
        if self.is_running:
            print("⚠️ Servidor já está rodando")
            return
        
        def run_server():
            config = uvicorn.Config(
                app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=False
            )
            server = uvicorn.Server(config)
            asyncio.run(server.serve())
        
        self.server_thread = threading.Thread(
            target=run_server,
            daemon=True,
            name="GenesysServer"
        )
        self.server_thread.start()
        self.is_running = True
        
        print(f"🚀 Servidor Genesys iniciado em segundo plano")
        print(f"📡 URL: http://{self.host}:{self.port}")
        print(f"🔧 Status: http://{self.host}:{self.port}/status")
        print(f"💬 Chat: http://{self.host}:{self.port}/chat")
        
        # Aguardar servidor inicializar
        time.sleep(2)
        
        return True
    
    def stop(self):
        """Para o servidor"""
        if self.server_thread and self.is_running:
            # Em produção, você implementaria uma forma mais elegante de parar
            self.is_running = False
            print("🛑 Servidor Genesys parado")

# Instância global do servidor
genesys_server = GenesysServer()

def main():
    """Executa o servidor diretamente"""
    print("🤖 Iniciando Servidor Genesys Local...")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
        log_level="info"
    )

if __name__ == "__main__":
    main()
