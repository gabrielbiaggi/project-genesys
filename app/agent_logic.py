# app/agent_logic.py
import os
from langchain.agents import AgentExecutor, create_react_agent
try:
    from langchain_community.llms import LlamaCpp
except ImportError:
    # Fallback para desenvolvimento sem llama-cpp-python
    LlamaCpp = None
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage

# Importar as ferramentas que definimos
from app.tools.file_system_tool import apply_file_change, list_files, read_file
from app.tools.terminal_tool import execute_terminal_command
from app.tools.web_search_tool import web_search

def create_genesys_agent():
    """
    Cria e configura o Agente Genesys com suas ferramentas, memória e lógica.
    """
    # --- Carregar Configurações do Modelo ---
    model_filename = os.getenv("MODEL_GGUF_FILENAME", "Llama-3-8B-Instruct-SP-32k-Q4_K_M.gguf")
    model_path = f"./models/{model_filename}"
    
    # Carregar o projetor multimodal, se existir e o arquivo for encontrado
    multimodal_projector_filename = os.getenv("MULTIMODAL_PROJECTOR_FILENAME", "")
    chat_handler = None
    llava_projector_path = f"./models/{multimodal_projector_filename}"
    if multimodal_projector_filename and os.path.exists(llava_projector_path):
        try:
            from langchain_community.llms.llava_cpp import LlavaCpp
            
            chat_handler = LlavaCpp(
                model_path=model_path,
                llava_projector_path=llava_projector_path,
                n_gpu_layers=-1,
                n_batch=512,
                n_ctx=4096,
                f16_kv=True,
                verbose=True,
            )
        except ImportError:
            print("AVISO: Falha ao importar LlavaCpp. A funcionalidade multimodal estará desativada.")
            print("Para ativar, instale as dependências corretas: pip install 'langchain-community[llava]'")
            chat_handler = None

    # --- Configuração LlamaCpp com GPU ATIVADA ---
    # n_gpu_layers=-1 significa TODAS as camadas na GPU para máxima performance
    # Performance esperada: 50-200+ tokens/segundo
    if LlamaCpp is None:
        raise ImportError("llama-cpp-python não está instalado. Execute: pip install llama-cpp-python")
    
    llm = LlamaCpp(
        model_path=model_path,
        n_gpu_layers=-1,     # 🎮 TODAS as camadas na GPU (máxima performance)
        n_batch=512,         # Tamanho do batch para processamento
        n_ctx=4096,          # Contexto máximo do modelo
        f16_kv=True,         # Usar FP16 para economizar VRAM
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        verbose=True,        # Mostrar informações de debug
    )

    # --- Definir as Ferramentas Disponíveis ---
    tools = [apply_file_change, list_files, read_file, execute_terminal_command, web_search]

    # --- Template de Prompt para o Agente ---
    template = """
    Você é o Agente Genesys, uma IA soberana. Responda ao humano da melhor forma que puder.
    Você tem acesso às seguintes ferramentas:

    {tools}

    Use o seguinte formato:

    Question: a pergunta de entrada que você deve responder
    Thought: você deve sempre pensar sobre o que fazer
    Action: a ação a ser tomada, deve ser uma de [{tool_names}]
    Action Input: a entrada para a ação
    Observation: o resultado da ação
    ... (este Thought/Action/Action Input/Observation pode se repetir N vezes)
    Thought: Eu agora sei a resposta final
    Final Answer: a resposta final para a pergunta original. Se a sua resposta for uma proposta de alteração de arquivo, o formato DEVE ser um JSON contendo 'diff' e 'new_content'. Exemplo: ```json{{"diff": "...", "new_content": "..."}}```

    Comece!

    Conversa Anterior:
    {chat_history}

    Question: {input}
    Thought:{agent_scratchpad}
    """
    
    prompt = PromptTemplate.from_template(template)

    # --- Memória do Agente ---
    memory = ConversationBufferWindowMemory(
        k=5, 
        memory_key="chat_history", 
        input_key='input', 
        output_key='output',
        return_messages=True # Retorna as mensagens para o log
    )
    
    # --- Criar o Agente ReAct ---
    agent = create_react_agent(llm, tools, prompt)
    
    # --- Criar o Executor do Agente ---
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        memory=memory,
        handle_parsing_errors=True,
        return_intermediate_steps=True # ESSENCIAL para ver o "pensamento" do agente
    )

    # Retorna tanto o executor do agente quanto o handler de chat multimodal, se existir
    return agent_executor, chat_handler

def create_multimodal_message(prompt: str, image_bytes: bytes):
    """Cria uma mensagem multimodal para o LLaVA."""
    return [
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_bytes.decode('utf-8')}",
                },
            ]
        )
    ]
