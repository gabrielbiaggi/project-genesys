# app/agent_logic.py
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# Importar as ferramentas que definimos
from app.tools.file_system_tool import propose_file_change, apply_file_change, list_files, read_file
from app.tools.terminal_tool import execute_terminal_command
from app.tools.web_search_tool import web_search

def create_genesys_agent():
    """
    Cria e configura o Agente Genesys com suas ferramentas, memória e lógica.
    """
    # --- Carregar Configurações do Modelo ---
    model_filename = os.getenv("MODEL_GGUF_FILENAME", "Llama-3-70B-Instruct.Q2_K.gguf")
    model_path = f"./models/{model_filename}"

    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    llm = LlamaCpp(
        model_path=model_path,
        n_gpu_layers=-1,
        n_batch=512,
        n_ctx=4096,
        f16_kv=True,
        callback_manager=callback_manager,
        verbose=True,
    )

    # --- Definir as Ferramentas Disponíveis ---
    # Removido write_file, substituído por propose e apply
    tools = [propose_file_change, apply_file_change, list_files, read_file, execute_terminal_command, web_search]

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

    return agent_executor
