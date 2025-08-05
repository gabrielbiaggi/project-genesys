# scripts/download_model.py
import os
import requests
from dotenv import load_dotenv
from tqdm import tqdm

# Carregar variáveis de ambiente
load_dotenv(dotenv_path='../.env')

MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_QUANTIZATION = os.getenv("MODEL_QUANTIZATION")
MODEL_FILENAME = f"{MODEL_NAME}.{MODEL_QUANTIZATION}.gguf"

# O repositório no Hugging Face que contém os modelos GGUF quantizados
# Usamos o repositório da "QuantFactory" que é um padrão da comunidade
HUGGING_FACE_REPO = f"QuantFactory/{MODEL_NAME}-GGUF"

# Construir a URL de download
DOWNLOAD_URL = f"https://huggingface.co/{HUGGING_FACE_REPO}/resolve/main/{MODEL_FILENAME}"

# Caminho onde os modelos serão salvos
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_FILENAME)

def download_model():
    """
    Baixa o modelo de IA do Hugging Face se ele ainda não existir.
    """
    if os.path.exists(MODEL_PATH):
        print(f"O modelo '{MODEL_FILENAME}' já existe em '{MODELS_DIR}'. Download pulado.")
        return

    print(f"Iniciando o download do modelo: {MODEL_FILENAME}")
    print(f"De: {DOWNLOAD_URL}")
    print(f"Para: {MODEL_PATH}")

    try:
        with requests.get(DOWNLOAD_URL, stream=True) as r:
            r.raise_for_status()
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte

            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(MODEL_PATH, 'wb') as f:
                for chunk in r.iter_content(chunk_size=block_size):
                    progress_bar.update(len(chunk))
                    f.write(chunk)
            progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERRO: Algo deu errado durante o download.")
            # Tentar remover o arquivo parcial
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
        else:
            print(f"Download do modelo '{MODEL_FILENAME}' concluído com sucesso!")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o modelo: {e}")
        # Tentar remover o arquivo parcial
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)

if __name__ == "__main__":
    download_model()
