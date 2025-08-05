# app/tools/file_system_tool.py
from langchain.tools import tool
import os

# Define um diretório de trabalho seguro para o agente.
# Ele só poderá ler/escrever arquivos dentro desta pasta.
# Isso é uma medida de segurança crucial.
SAFE_WORKSPACE = os.path.join(os.path.dirname(__file__), '..', '..', 'workspace')
os.makedirs(SAFE_WORKSPACE, exist_ok=True)

@tool("ReadFile")
def read_file(file_path: str) -> str:
    """
    Lê o conteúdo de um arquivo especificado.
    Só pode acessar arquivos dentro do diretório de trabalho seguro.
    """
    safe_file_path = os.path.join(SAFE_WORKSPACE, file_path)
    if not os.path.abspath(safe_file_path).startswith(os.path.abspath(SAFE_WORKSPACE)):
        return "Erro: Acesso negado. Tentativa de ler arquivo fora do workspace seguro."
    
    try:
        with open(safe_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Erro: O arquivo '{file_path}' não foi encontrado."
    except Exception as e:
        return f"Erro ao ler o arquivo: {e}"

@tool("WriteFile")
def write_file(file_path: str, content: str) -> str:
    """
    Escreve ou sobrescreve o conteúdo de um arquivo especificado.
    Só pode criar ou modificar arquivos dentro do diretório de trabalho seguro.
    """
    safe_file_path = os.path.join(SAFE_WORKSPACE, file_path)
    if not os.path.abspath(safe_file_path).startswith(os.path.abspath(SAFE_WORKSPACE)):
        return "Erro: Acesso negado. Tentativa de escrever arquivo fora do workspace seguro."
        
    try:
        with open(safe_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Arquivo '{file_path}' escrito com sucesso."
    except Exception as e:
        return f"Erro ao escrever o arquivo: {e}"

# Para a Fase 3, estas ferramentas seriam importadas e disponibilizadas para um Agente LangChain.
