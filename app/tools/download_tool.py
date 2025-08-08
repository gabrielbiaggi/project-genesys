# app/tools/download_tool.py
import os
import requests
from dotenv import load_dotenv
from tqdm import tqdm
from langchain.tools import tool

# Carrega as variáveis de ambiente do .env na raiz do projeto
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Caminho onde os modelos serão salvos, relativo à raiz do projeto
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

def _download_file_logic(filename: str, repo_id: str):
    """
    Lógica interna de download. Não é uma ferramenta LangChain.
    """
    if not filename or not repo_id:
        return f"AVISO: Nome do arquivo ou ID do repositório não fornecido. Download pulado."
        
    file_path = os.path.join(MODELS_DIR, filename)
    download_url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    
    if os.path.exists(file_path):
        return f"O arquivo '{filename}' já existe. Download pulado."

    # Prepara o cabeçalho de autenticação
    hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN")
    headers = {}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    else:
        print(f"AVISO: HUGGING_FACE_HUB_TOKEN não encontrado. O download pode falhar se o repositório for privado ou exigir login.")

    try:
        print(f"Iniciando download de: {filename}")
        with requests.get(download_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(file_path, 'wb') as f, tqdm(total=total_size, unit='iB', unit_scale=True, desc=filename) as pbar:
                for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"Download de '{filename}' concluído com sucesso!")
        return f"Download de '{filename}' concluído com sucesso!"

    except Exception as e:
        # Limpa o arquivo parcial em caso de erro
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Erro durante o download de '{filename}': {e}")
        return f"Erro durante o download de '{filename}': {e}"

@tool("DownloadModel")
def download_model_tool():
    """
    Baixa o modelo de IA e o projetor multimodal especificados no arquivo .env.
    Esta ferramenta lê as variáveis de ambiente para determinar quais arquivos baixar.
    """
    repo_id = os.getenv("HUGGING_FACE_REPO_ID")
    model_filename = os.getenv("MODEL_GGUF_FILENAME")
    projector_filename = os.getenv("MULTIMODAL_PROJECTOR_FILENAME")

    results = []
    
    # Baixar o modelo principal
    model_result = _download_file_logic(model_filename, repo_id)
    results.append(model_result)
    
    # Baixar o projetor multimodal, se especificado
    if projector_filename:
        projector_result = _download_file_logic(projector_filename, repo_id)
        results.append(projector_result)
        
    return "\n".join(results)
