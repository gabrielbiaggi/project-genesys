# scripts/test_model_load.py
import os
import sys

# Garante que o diretório raiz do projeto esteja no path para as importações
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv

def test_load():
    """
    Tenta carregar o agente Gênesis para diagnosticar problemas de inicialização.
    """
    print("--- INICIANDO TESTE DE CARGA DO MODELO ---")
    
    # Carrega as mesmas variáveis de ambiente que a API usaria
    load_dotenv(dotenv_path=os.path.join(project_root, '.env'))
    
    model_file = os.getenv("MODEL_GGUF_FILENAME")
    projector_file = os.getenv("MULTIMODAL_PROJECTOR_FILENAME")
    
    print(f"Modelo a ser carregado: {model_file}")
    print(f"Projetor a ser carregado: {projector_file}")

    model_path = os.path.join(project_root, 'models', model_file)
    
    if not os.path.exists(model_path):
        print(f"ERRO CRÍTICO: O arquivo do modelo não foi encontrado em '{model_path}'")
        print("Execute o download do modelo antes de continuar.")
        return

    try:
        from app.agent_logic import create_genesys_agent
        print("Importado 'create_genesys_agent' com sucesso.")
        print("Tentando instanciar o agente...")
        
        agent, handler = create_genesys_agent()
        
        if agent is not None:
            print("SUCESSO: Agente Gênesis carregado com sucesso!")
        else:
            print("FALHA: A função create_genesys_agent() retornou None.")

    except Exception as e:
        print("\n--- ERRO CAPTURADO DURANTE A INICIALIZAÇÃO DO AGENTE ---")
        import traceback
        traceback.print_exc()
        print("---------------------------------------------------------")

if __name__ == "__main__":
    test_load()
