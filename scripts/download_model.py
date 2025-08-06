# scripts/download_model.py
import os
import requests
from dotenv import load_dotenv
from tqdm import tqdm

# Carregar variáveis de ambiente de um arquivo .env se ele existir
load_dotenv(dotenv_path='../.env')

# --- CONFIGURAÇÃO DO MODELO ---
# Altere estes valores para baixar um modelo diferente.
# O repositório no Hugging Face que contém os modelos GGUF quantizados.
HUGGING_FACE_REPO_ID = os.getenv("HUGGING_FACE_REPO_ID", "mindrage/Llama-3-70B-Instruct-v2-LLaVA-GGUF")
# O nome exato do arquivo .gguf a ser baixado.
MODEL_GGUF_FILENAME = os.getenv("MODEL_GGUF_FILENAME", "Llama-3-70B-Instruct-v2-Q4_K_M.gguf")

# --- CONFIGURAÇÃO MULTIMODAL (para LLaVA) ---
# Se o modelo for multimodal (como o LLaVA), especifique o arquivo do projetor.
# Deixe como "" se o modelo for apenas texto.
MULTIMODAL_PROJECTOR_FILENAME = os.getenv("MULTIMODAL_PROJECTOR_FILENAME", "mmproj-Llama-3-70B-Instruct-v2-f16.gguf")
# --- FIM DA CONFIGURAÇÃO ---


# Caminho onde os modelos serão salvos
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

def download_file(filename: str, repo_id: str):
    """
    Baixa um arquivo específico do Hugging Face se ele ainda não existir.
    """
    if not filename:
        return
        
    file_path = os.path.join(MODELS_DIR, filename)
    download_url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    
    if os.path.exists(file_path):
        print(f"O arquivo '{filename}' já existe em '{MODELS_DIR}'. Download pulado.")
        return

    print(f"Iniciando o download do arquivo: {filename}")
    print(f"Do repositório: {repo_id}")
    print(f"Salvando em: {file_path}")

    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            block_size = 1024 * 1024  # 1 MB

            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=filename)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=block_size):
                    progress_bar.update(len(chunk))
                    f.write(chunk)
            progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print(f"ERRO: O tamanho do arquivo baixado '{filename}' não corresponde ao esperado. Excluindo arquivo parcial.")
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            print(f"Download do arquivo '{filename}' concluído com sucesso!")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo '{filename}': {e}")
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    # Baixar o modelo principal
    download_file(MODEL_GGUF_FILENAME, HUGGING_FACE_REPO_ID)
    
    # Baixar o projetor multimodal, se especificado
    if MULTIMODAL_PROJECTOR_FILENAME:
        download_file(MULTIMODAL_PROJECTOR_FILENAME, HUGGING_FACE_REPO_ID)
