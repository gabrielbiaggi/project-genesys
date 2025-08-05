# scripts/download_model.py
import os
import requests
from dotenv import load_dotenv
from tqdm import tqdm

# Carregar variáveis de ambiente de um arquivo .env se ele existir
# Isso torna a configuração mais flexível, mas também funciona sem ele.
load_dotenv(dotenv_path='../.env')

# --- CONFIGURAÇÃO DO MODELO ---
# Altere estes valores para baixar um modelo diferente.
# O repositório no Hugging Face que contém os modelos GGUF quantizados.
# Ex: "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF"
HUGGING_FACE_REPO_ID = os.getenv("HUGGING_FACE_REPO_ID", "ikawrakow/Meta-Llama-3-70B-Instruct-GGUF")

# O nome exato do arquivo .gguf a ser baixado.
# Ex: "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
# Para 70B em hardware limitado, Q2_K ou Q3_K_S são recomendados.
MODEL_GGUF_FILENAME = os.getenv("MODEL_GGUF_FILENAME", "Llama-3-70B-Instruct.Q2_K.gguf")
# --- FIM DA CONFIGURAÇÃO ---


# Construir a URL de download a partir do repositório e nome do arquivo
DOWNLOAD_URL = f"https://huggingface.co/{HUGGING_FACE_REPO_ID}/resolve/main/{MODEL_GGUF_FILENAME}"

# Caminho onde os modelos serão salvos
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_GGUF_FILENAME)

def download_model():
    """
    Baixa o modelo de IA do Hugging Face se ele ainda não existir.
    """
    if os.path.exists(MODEL_PATH):
        print(f"O modelo '{MODEL_GGUF_FILENAME}' já existe em '{MODELS_DIR}'. Download pulado.")
        return

    print(f"Iniciando o download do modelo: {MODEL_GGUF_FILENAME}")
    print(f"Do repositório: {HUGGING_FACE_REPO_ID}")
    print(f"URL de download: {DOWNLOAD_URL}")
    print(f"Salvando em: {MODEL_PATH}")

    try:
        with requests.get(DOWNLOAD_URL, stream=True) as r:
            r.raise_for_status()
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            block_size = 1024 * 1024  # 1 MB para eficiência em arquivos grandes

            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=MODEL_GGUF_FILENAME)
            with open(MODEL_PATH, 'wb') as f:
                for chunk in r.iter_content(chunk_size=block_size):
                    progress_bar.update(len(chunk))
                    f.write(chunk)
            progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERRO: O tamanho do arquivo baixado não corresponde ao esperado. Excluindo arquivo parcial.")
            # Tentar remover o arquivo parcial
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
        else:
            print(f"Download do modelo '{MODEL_GGUF_FILENAME}' concluído com sucesso!")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o modelo: {e}")
        # Tentar remover o arquivo parcial
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)

if __name__ == "__main__":
    download_model()
