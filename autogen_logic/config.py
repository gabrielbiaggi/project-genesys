# autogen_logic/config.py
import os
from dotenv import load_dotenv

def get_config_list():
    """
    Carrega a configuração dos modelos LLM a partir de variáveis de ambiente.
    Isso permite configurar múltiplos modelos, como o Gênesis local e o Gemini da Google.
    """
    # Carrega as variáveis do arquivo .env na raiz do projeto
    load_dotenv(dotenv_path='../.env')

    # Configuração para o modelo local (seu Gênesis)
    # Supondo que você o exponha através de uma API compatível com a OpenAI, como o LM Studio ou Oobabooga
    local_model_endpoint = os.getenv("LOCAL_MODEL_ENDPOINT", "http://localhost:11434/v1")
    
    # Configuração para o Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    config_list = [
        {
            "model": "genesys_local", # Nome que usaremos para se referir ao seu modelo local
            "base_url": local_model_endpoint,
            "api_type": "open_ai",
            "api_key": "NULL", # Chave de API não necessária para o endpoint local
        }
    ]

    # Adiciona a configuração do Gemini apenas se a chave de API estiver disponível
    if gemini_api_key:
        config_list.append(
            {
                "model": "gemini-1.5-pro-latest", # Ou o modelo Gemini que você preferir
                "api_key": gemini_api_key,
                "api_type": "google",
            }
        )
    
    return config_list

