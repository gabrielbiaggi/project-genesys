# genesys_integration/genesys_agent.py
"""
Agente Genesys integrado ao Agent-MCP
Executa o modelo LLaMA 70B com processamento de imagens localmente
"""
import os
import sys
import asyncio
import json
import base64
import threading
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

import google.generativeai as genai

# Importações para o modelo LLaMA
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from langchain_community.llms import LlamaCpp
    from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("⚠️ Dependências do LLaMA não instaladas. Use: pip install -r requirements_genesys.txt")

# Importações das ferramentas da Genesys original
try:
    sys.path.append(str(Path(__file__).parent.parent / "C:\\DEVBill\\Projetos\\Genesys"))
    from app.tools.file_system_tool import apply_file_change, list_files, read_file
    from app.tools.terminal_tool import execute_terminal_command
    from app.tools.web_search_tool import web_search
    GENESYS_TOOLS_AVAILABLE = True
except ImportError:
    GENESYS_TOOLS_AVAILABLE = False
    print("⚠️ Ferramentas da Genesys não encontradas. Usando versões mockadas.")

import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .tools import TOOL_DEFINITIONS, execute_tool

# --- Prompts ---

ERROR_CORRECTION_PROMPT = """
Você é um especialista em depuração de software. Uma ferramenta executada anteriormente falhou.
Sua tarefa é analisar o erro e a tarefa original para fornecer uma solução.

Tarefa Original:
{original_task}

Ferramenta Invocada (formato JSON):
{tool_call_json}

Erro Recebido:
{error_message}

Contexto Adicional:
- O ambiente de execução é Windows.
- As ferramentas disponíveis incluem um sistema de arquivos (`read_file`, `list_files`, `write_file`) e pesquisa na web (`web_search`).

Análise e Plano de Ação:
1.  **Diagnóstico**: Qual é a causa provável do erro? (Ex: arquivo não encontrado, comando inválido, problema de permissão, etc.)
2.  **Pesquisa (se necessário)**: Se a causa não for óbvia, formule uma consulta de pesquisa para a ferramenta `web_search` para encontrar soluções.
3.  **Solução Proposta**: Com base na sua análise e/ou pesquisa, proponha uma nova chamada de ferramenta corrigida ou uma abordagem alternativa para cumprir a tarefa original. A resposta DEVE ser uma chamada de ferramenta em formato JSON, como `{"tool": "web_search", "args": {"query": "como resolver X"}}` ou `{"tool": "read_file", "args": {"file_path": "C:\\path\\correto\\arquivo.txt"}}`.
4.  **Se Nenhuma Solução For Encontrada**: Se não for possível corrigir, responda com uma explicação clara do problema e por que não pode ser resolvido.

Sua resposta final deve ser APENAS a chamada de ferramenta corrigida em JSON ou a explicação.
"""

class GenesysAgent:
    """O agente principal que carrega um modelo local e interage com ferramentas."""
    
    def __init__(self, model_path: str = None, use_gpu: bool = True):
        self.agent_id = "genesys_master"
        self.specializations = ["coding", "multimodal", "system_integration", "ai_orchestration"]
        self.model_path = model_path or self._get_model_path()
        self.use_gpu = use_gpu
        self.model = None
        self.tokenizer = None
        self.llama_cpp = None
        self.is_loaded = False
        self.tools = self._setup_tools()
        self.gemini_model = None
        
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Configurar Gemini
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')
                print("✅ API do Gemini configurada com sucesso!")
            except Exception as e:
                print(f"⚠️ Erro ao configurar a API do Gemini: {e}")
        else:
            print("⚠️ GEMINI_API_KEY não encontrada no .env. Funções avançadas desativadas.")
        
    def _get_model_path(self) -> str:
        """Determina o caminho do modelo baseado na configuração"""
        # Primeiro, tentar usar o modelo da Genesys original
        genesys_model = os.getenv("MODEL_GGUF_FILENAME", "llama-3-70b-instruct.Q4_K_M.gguf")
        genesys_path = f"C:\\DEVBill\\Projetos\\Genesys\\models\\{genesys_model}"
        
        if os.path.exists(genesys_path):
            return genesys_path
        
        # Fallback para modelo local no projeto
        local_model = Path(__file__).parent / "models" / genesys_model
        if local_model.exists():
            return str(local_model)
        
        # Se não encontrar, usar o modelo padrão
        return f"./genesys_integration/models/{genesys_model}"
    
    def _setup_tools(self) -> Dict[str, Any]:
        """Carrega e configura as ferramentas disponíveis."""
        self.tool_definitions = TOOL_DEFINITIONS
        self.tool_executor = execute_tool
        # Mapeamento para fácil acesso, se necessário
        self.tools = {tool['name']: tool for tool in self.tool_definitions}
        print(f"✅ Ferramentas configuradas: {', '.join(self.tools.keys())}")
        return self.tools
    
    def _create_mock_tools(self) -> Dict[str, Any]:
        """DEPRECATED: Mantido para compatibilidade, mas _setup_tools é o preferido."""
        print("⚠️ _create_mock_tools está obsoleto. Usando _setup_tools.")
        return self._setup_tools()
    
    async def load_model(self) -> bool:
        """Carrega o modelo de linguagem local (GGUF) usando LlamaCpp."""
        if not LLAMA_AVAILABLE:
            print("❌ Dependências do LLaMA não disponíveis")
            return False
        
        if self.is_loaded:
            return True
        
        print(f"🤖 Carregando Genesys (LLaMA 70B)...")
        print(f"📁 Caminho do modelo: {self.model_path}")
        
        try:
            # Usar llama-cpp-python para melhor performance com GPU
            if os.path.exists(self.model_path):
                self.llama_cpp = LlamaCpp(
                    model_path=self.model_path,
                    n_gpu_layers=-1 if self.use_gpu else 0,
                    n_batch=512,
                    n_ctx=4096,
                    f16_kv=True,
                    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                    verbose=False,
                    temperature=0.7,
                )
                self.is_loaded = True
                print("✅ Genesys carregada com sucesso!")
                return True
            else:
                print(f"❌ Modelo não encontrado em: {self.model_path}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            return False
            
    def _should_use_gemini(self, task: str) -> bool:
        """Determina se a tarefa é complexa o suficiente para usar a API do Gemini."""
        if not self.gemini_model:
            return False
        
        complex_keywords = [
            "analise", "refatore", "arquitetura", "explique detalhadamente", 
            "crie um plano", "projete", "melhore este código", "auditoria",
            "implemente a seguinte feature", "escreva um teste completo"
        ]
        
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in complex_keywords)

    async def _call_gemini_api(self, prompt: str) -> str:
        """Chama a API do Gemini com o prompt fornecido."""
        print("🧠 Tarefa complexa detectada. Usando API do Gemini...")
        try:
            response = await self.gemini_model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Erro ao chamar a API do Gemini: {e}")
            return f"Erro ao processar com Gemini: {e}"
    
    async def process_task(self, task: str, context: Dict = None, use_tools: bool = True) -> str:
        """Processa uma tarefa usando o modelo Genesys ou a API do Gemini."""
        
        specialized_prompt = self._create_specialized_prompt(task, context, use_tools)
        
        # Lógica de decisão: Usar Gemini para tarefas complexas
        if self._should_use_gemini(task):
            return await self._call_gemini_api(specialized_prompt)

        # Lógica original para usar o modelo local
        if not self.is_loaded:
            await self.load_model()
        
        if not self.is_loaded:
            return "❌ Modelo Genesys não está carregado"
        
        try:
            # Usar llama-cpp-python
            response = self.llama_cpp(specialized_prompt)
            
            # Se a resposta indica uso de ferramenta, executar
            if use_tools and self._should_use_tools(response):
                tool_response = await self._execute_tools(response, task)
                return f"{response}\n\n🔧 **Resultado das Ferramentas:**\n{tool_response}"
            
            return response
            
        except Exception as e:
            return f"❌ Erro no processamento local: {str(e)}"
    
    def _create_specialized_prompt(self, task: str, context: Dict = None, use_tools: bool = True) -> str:
        """Cria prompt especializado baseado no contexto"""
        base_prompt = f"""🤖 **AGENTE GENESYS MASTER**
ID: {self.agent_id}
Especializações: {', '.join(self.specializations)}

CONTEXTO DO PROJETO: Agent-MCP - Sistema de orquestração multi-agente
MEU PAPEL: Agente especialista master com modelo LLaMA 70B local

TAREFA RECEBIDA: {task}

CONTEXTO ADICIONAL: {json.dumps(context, indent=2) if context else 'Nenhum'}

FERRAMENTAS DISPONÍVEIS: {'Ativadas' if use_tools else 'Desativadas'}
- file_system: Modificar arquivos
- list_files: Listar diretórios
- read_file: Ler arquivos
- terminal: Executar comandos
- web_search: Buscar na web

INSTRUÇÕES:
1. Analise a tarefa cuidadosamente
2. Use ferramentas quando necessário
3. Forneça respostas técnicas detalhadas
4. Coordene com outros agentes via Agent-MCP
5. Mantenha foco em código e implementação

RESPOSTA:
"""
        return base_prompt
    
    def _should_use_tools(self, response: str) -> bool:
        """Determina se a resposta indica necessidade de usar ferramentas"""
        tool_indicators = [
            "usar ferramenta", "executar comando", "ler arquivo", 
            "modificar arquivo", "buscar na web", "listar arquivos"
        ]
        return any(indicator in response.lower() for indicator in tool_indicators)
    
    async def _execute_tools(self, response: str, original_task: str) -> str:
        """Analisa a resposta do modelo, executa a ferramenta e retorna o resultado."""
        try:
            # Extrai o JSON da chamada da ferramenta da resposta do modelo
            tool_call_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not tool_call_match:
                return "Não foi possível extrair a chamada da ferramenta da resposta."

            tool_call_json = tool_call_match.group(0)
            tool_data = json.loads(tool_call_json)
            tool_name = tool_data.get("tool")
            tool_args = tool_data.get("args", {})

            if not tool_name:
                return "Nome da ferramenta não especificado na chamada."

            print(f"▶️ Executando ferramenta: {tool_name} com args: {tool_args}")
            # A função execute_tool agora é assíncrona
            result = await self.tool_executor(tool_name, tool_args)
            print(f"◀️ Resultado da ferramenta: {result[:200]}...")
            return result

        except Exception as e:
            print(f"❌ Erro ao executar a ferramenta: {e}")

            # --- CICLO DE AUTO-CORREÇÃO ---
            if self.gemini_model:
                print("🧠 Iniciando ciclo de auto-correção com a API do Gemini...")
                
                # Tenta obter o JSON da chamada da ferramenta, mesmo que tenha falhado
                tool_call_json_for_prompt = "N/A"
                try:
                    tool_call_json_for_prompt = json.dumps(json.loads(re.search(r'\{.*\}', response, re.DOTALL).group(0)))
                except:
                    pass # Mantém "N/A" se a extração falhar

                correction_prompt = ERROR_CORRECTION_PROMPT.format(
                    original_task=original_task,
                    tool_call_json=tool_call_json_for_prompt,
                    error_message=str(e)
                )

                # Chama o Gemini para obter uma sugestão de correção
                correction_suggestion = await self._call_gemini_api(correction_prompt)
                
                print(f"💡 Sugestão de correção do Gemini: {correction_suggestion}")
                
                # Verifica se a sugestão é uma nova chamada de ferramenta e a executa
                if 'tool' in correction_suggestion and 'args' in correction_suggestion:
                    print("🔁 Tentando executar a chamada de ferramenta corrigida...")
                    # Chama a si mesmo recursivamente com a sugestão corrigida
                    return await self._execute_tools(correction_suggestion, original_task)
                else:
                    # Se a sugestão não for uma ferramenta, retorna a explicação do Gemini
                    return f"Análise do Gemini sobre o erro: {correction_suggestion}"

            return f"Erro final ao executar a ferramenta (sem auto-correção): {e}"

    async def process_multimodal(self, text: str, image_data: str = None) -> str:
        """Processa entradas multimodais (texto e imagem)."""
        if not image_data:
            return await self.process_task(text)
        
        # Para processamento de imagem, você precisaria integrar com LLaVA ou similar
        # Por agora, retornamos processamento apenas de texto
        enhanced_prompt = f"""
🖼️ **PROCESSAMENTO MULTIMODAL**

TEXTO: {text}
IMAGEM: {'Fornecida (Base64)' if image_data else 'Não fornecida'}

Análise da imagem fornecida juntamente com o texto...
"""
        return await self.process_task(enhanced_prompt)
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do agente"""
        return {
            "agent_id": self.agent_id,
            "specializations": self.specializations,
            "model_loaded": self.is_loaded,
            "model_path": self.model_path,
            "gpu_enabled": self.use_gpu,
            "tools_available": GENESYS_TOOLS_AVAILABLE,
            "llama_available": LLAMA_AVAILABLE
        }

# Instância global do agente
genesys_agent = GenesysAgent()

async def main():
    """Função principal para testes"""
    print("🧪 Testando Agente Genesys...")
    
    # Carregar modelo
    await genesys_agent.load_model()
    
    # Teste básico
    response = await genesys_agent.process_task(
        "Analise a estrutura do projeto Agent-MCP e sugira melhorias"
    )
    print(f"Resposta: {response}")
    
    # Status
    status = genesys_agent.get_status()
    print(f"Status: {json.dumps(status, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
