# autogen_logic/tools/code_tools.py
import os

# Define o diretório de trabalho seguro, relativo à raiz do projeto
# Isso garante que as ferramentas só acessem o código que permitimos
SAFE_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'workspace'))

def read_code_file(file_path: str) -> str:
    """
    Lê o conteúdo de um arquivo de código especificado dentro do workspace seguro.
    
    Args:
        file_path (str): O caminho relativo do arquivo a ser lido, a partir da pasta 'workspace'.
        
    Returns:
        str: O conteúdo do arquivo ou uma mensagem de erro.
    """
    # Constrói o caminho completo e seguro para o arquivo
    safe_file_path = os.path.join(SAFE_WORKSPACE, file_path)
    
    # Validação de segurança crucial para prevenir ataques de "Directory Traversal"
    if not os.path.abspath(safe_file_path).startswith(SAFE_WORKSPACE):
        return "Erro: Acesso negado. Tentativa de ler arquivo fora do workspace seguro."
    
    try:
        with open(safe_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Erro: O arquivo '{file_path}' não foi encontrado no workspace."
    except Exception as e:
        return f"Erro ao ler o arquivo: {str(e)}"


