# app/tools/file_system_tool.py
from langchain.tools import tool
import os
import difflib

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

@tool("ListFiles")
def list_files(path: str) -> list:
    """Lista arquivos e diretórios recursivamente dentro do workspace seguro."""
    base_path = os.path.join(SAFE_WORKSPACE, path)
    if not os.path.abspath(base_path).startswith(os.path.abspath(SAFE_WORKSPACE)):
        return ["Erro: Acesso negado."]

    try:
        paths = []
        for root, dirs, files in os.walk(base_path):
            relative_root = os.path.relpath(root, SAFE_WORKSPACE)
            if relative_root == '.':
                relative_root = ''
            for name in dirs:
                paths.append(os.path.join(relative_root, name))
            for name in files:
                paths.append(os.path.join(relative_root, name))
        return sorted(paths)
    except Exception as e:
        return [f"Erro ao listar arquivos: {e}"]

@tool("ApplyFileChange")
def apply_file_change(path: str, new_content: str) -> str:
    """
    Escreve (aplica) o conteúdo em um arquivo dentro do workspace seguro.
    Cria diretórios se necessário.
    """
    safe_file_path = os.path.join(SAFE_WORKSPACE, path)
    if not os.path.abspath(safe_file_path).startswith(os.path.abspath(SAFE_WORKSPACE)):
        return "Erro: Acesso negado. Tentativa de escrever arquivo fora do workspace seguro."

    try:
        os.makedirs(os.path.dirname(safe_file_path), exist_ok=True)
        with open(safe_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"Arquivo '{path}' salvo com sucesso."
    except Exception as e:
        return f"Erro ao escrever o arquivo: {e}"

@tool("WriteFile")
def write_file(file_path: str, content: str) -> str:
    """
    Mantido por compatibilidade. Encaminha para apply_file_change.
    """
    return apply_file_change(file_path, content)

# Para a Fase 3, estas ferramentas seriam importadas e disponibilizadas para um Agente LangChain.
