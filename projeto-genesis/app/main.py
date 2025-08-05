from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Instanciar a aplicação FastAPI
app = FastAPI(
    title="Projeto Gênesys",
    description="A infraestrutura para um agente de IA soberano.",
    version="0.1.0",
)

@app.get("/", tags=["Status"])
async def root():
    """
    Endpoint principal para verificar o status da API.
    """
    return {"message": f"Bem-vindo ao Projeto Gênesys. O modelo '{os.getenv('MODEL_NAME')}' está aguardando ordens."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", 8000)))
