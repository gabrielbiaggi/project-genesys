# scripts/download_model.py
import os
import argparse
import requests
from dotenv import load_dotenv
from tqdm import tqdm

# Constrói um caminho absoluto para o arquivo .env na raiz do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

# --- CONFIGURAÇÃO PADRÃO DO MODELO ---
DEFAULT_REPO_ID = "MaziyarGhasemi/Meta-Llama-3-8B-Instruct-GGUF"
DEFAULT_FILENAME = "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"

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

    hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN")
    headers = {}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    else:
        print(f"AVISO: HUGGING_FACE_HUB_TOKEN não encontrado. O download pode falhar se o repositório for privado.")

    print(f"Iniciando o download do arquivo: {filename}")
    print(f"Do repositório: {repo_id}")
    print(f"Salvando em: {file_path}")

    try:
        with requests.get(download_url, headers=headers, stream=True) as r:
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
    parser = argparse.ArgumentParser(description="Baixar modelo GGUF do Hugging Face.")
    parser.add_argument("--repo_id", type=str, default=DEFAULT_REPO_ID, help="O ID do repositório no Hugging Face.")
    parser.add_argument("--filename", type=str, default=DEFAULT_FILENAME, help="O nome do arquivo .gguf a ser baixado.")
    
    args = parser.parse_args()
    
    download_file(args.filename, args.repo_id)

