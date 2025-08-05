# app/agent_logic.py
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# Importar as ferramentas que definimos
from app.tools.file_system_tool import read_file, write_file
from app.tools.terminal_tool import execute_terminal_command
from app.tools.web_search_tool import web_search

def create_genesis_agent():
    """
    Cria e configura o Agente Gênesys com suas ferramentas, memória e lógica.
    """
    # --- Carregar Configurações do Modelo ---
    model_name = os.getenv("MODEL_NAME")
    model_quantization = os.getenv("MODEL_QUANTIZATION")
    model_path = f"./models/{model_name}.{model_quantization}.gguf"

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
    tools = [read_file, write_file, execute_terminal_command, web_search]

    # --- Template de Prompt para o Agente ---
    # Este é mais complexo, pois ensina o agente a usar ferramentas.
    template = """
    Você é o Agente Gênesys, uma IA soberana. Responda ao humano da melhor forma que puder.
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
    Final Answer: a resposta final para a pergunta original

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
        output_key='output'
    )
    
    # --- Criar o Agente ReAct ---
    # ReAct é uma estratégia que permite ao modelo Raciocinar (Thought) e Agir (Action).
    agent = create_react_agent(llm, tools, prompt)
    
    # --- Criar o Executor do Agente ---
    # O Executor é o loop que executa o agente e suas ferramentas.
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        memory=memory,
        handle_parsing_errors=True # Lida com eventuais erros de formatação do LLM
    )

    return agent_executor
