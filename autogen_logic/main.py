# autogen_logic/main.py
import autogen
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Importações locais do nosso novo módulo
from .config import get_config_list
from .tools.code_tools import read_code_file

# --- Configuração da Aplicação FastAPI ---
app = FastAPI(
    title="Servidor de Orquestração Genesys com AutoGen",
    description="Uma API para interagir com agentes de IA colaborativos.",
    version="1.0.0",
)

# --- Carregamento e Configuração dos Agentes ---
try:
    config_list = get_config_list()
    
    # Configuração comum para os LLMs
    llm_config = {
        "config_list": config_list,
        "cache_seed": 42, # Usar 'None' para desativar o cache de respostas
    }

    # 1. Agente Assistente para o Genesys Local
    genesys_agent = autogen.AssistantAgent(
        name="Genesys_Local_Expert",
        system_message="""Você é Genesys, um especialista em programação focado neste projeto.
        Seu objetivo é fornecer respostas precisas, eficientes e seguras.
        Quando solicitado a ler um arquivo, use a ferramenta 'read_code_file'.
        Sempre coloque o código em blocos ```linguagem ... ```.""",
        llm_config=llm_config,
    )

    # 2. Agente Assistente para o Gemini
    gemini_agent = autogen.AssistantAgent(
        name="Gemini_Pro_Consultant",
        system_message="""Você é um consultor de IA da Google, especializado em otimização de código,
        boas práticas e arquiteturas de software em larga escala.
        Use a ferramenta 'read_code_file' se precisar ver o código-fonte.""",
        llm_config=llm_config,
    )

    # 3. Agente Proxy do Usuário (representa você)
    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER", # Não vai pedir input humano no meio do processo
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False, # Não executa código por padrão por segurança
        system_message="Um proxy humano. Você intermedeia a conversa."
    )
    
    # Registra a função como uma ferramenta para os agentes
    # Isso permite que eles chamem 'read_code_file' quando pensarem ser necessário
    user_proxy.register_function(
        function_map={
            "read_code_file": read_code_file
        }
    )
    genesys_agent.register_function(
        function_map={
            "read_code_file": read_code_file
        }
    )
    gemini_agent.register_function(
        function_map={
            "read_code_file": read_code_file
        }
    )

    print("Agentes configurados com sucesso.")

except Exception as e:
    print(f"Erro ao configurar os agentes: {e}")
    # Define os agentes como None para que a API possa retornar um erro apropriado
    genesys_agent = None
    gemini_agent = None
    user_proxy = None


# --- Modelos de Dados Pydantic para a API ---
class ChatRequest(BaseModel):
    prompt: str
    agent_name: str # "genesys" ou "gemini"

class DebateRequest(BaseModel):
    topic: str


# --- Endpoints da API ---

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Inicia um chat direto com um dos agentes.
    """
    if not user_proxy or not genesys_agent or not gemini_agent:
        raise HTTPException(status_code=500, detail="Agentes não foram inicializados corretamente.")

    if request.agent_name.lower() == "genesys":
        target_agent = genesys_agent
    elif request.agent_name.lower() == "gemini":
        target_agent = gemini_agent
    else:
        raise HTTPException(status_code=400, detail="Nome de agente inválido. Use 'genesys' ou 'gemini'.")

    user_proxy.initiate_chat(
        target_agent,
        message=request.prompt,
        clear_history=True
    )
    
    # A resposta final estará na última mensagem do histórico do agente
    last_message = target_agent.last_message(user_proxy)
    return {"response": last_message['content']}


@app.post("/debate")
async def debate(request: DebateRequest):
    """
    Inicia um debate entre o Genesys e o Gemini sobre um tópico.
    """
    if not user_proxy or not genesys_agent or not gemini_agent:
        raise HTTPException(status_code=500, detail="Agentes não foram inicializados corretamente.")

    # Criamos um GroupChat para orquestrar a conversa
    groupchat = autogen.GroupChat(
        agents=[user_proxy, genesys_agent, gemini_agent], 
        messages=[], 
        max_round=12
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # O user_proxy inicia o debate com o tópico fornecido
    user_proxy.initiate_chat(
        manager,
        message=request.topic,
    )
    
    return {"response": groupchat.messages}


if __name__ == "__main__":
    import uvicorn
    # Para executar este arquivo diretamente para teste:
    # uvicorn autogen_logic.main:app --host 0.0.0.0 --port 8003 --reload
    uvicorn.run(app, host="0.0.0.0", port=8003)

