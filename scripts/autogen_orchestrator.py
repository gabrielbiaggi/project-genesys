"""
scripts/autogen_orchestrator.py

Orquestrador básico usando AutoGen para:
- conversar com uma IA local (Llama.cpp/LLaVA) via REST (FastAPI deste projeto)
- ler/escrever arquivos no workspace
- opcional: consultar modelos externos (Claude/GPT/Gemini) para comparação

Execução:
  python scripts/autogen_orchestrator.py
  python scripts/autogen_orchestrator.py --cpu-only
"""

import argparse
import json
import os
import time
from typing import Optional

import requests
from tqdm import tqdm

# Nota: autogen-agentchat é modular; aqui usamos somente padrões básicos
try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
except Exception:
    AssistantAgent = None
    RoundRobinGroupChat = None


API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8002))
CHAT_API_URL = f"http://{API_HOST}:{API_PORT}/chat"

SAFE_WORKSPACE = os.path.join(os.path.dirname(__file__), '..', 'workspace')
SAFE_WORKSPACE = os.path.abspath(SAFE_WORKSPACE)
os.makedirs(SAFE_WORKSPACE, exist_ok=True)


def call_local_agent(prompt: str, image_b64: Optional[str] = None) -> dict:
    payload = {"prompt": prompt}
    if image_b64:
        payload["image"] = image_b64
    try:
        resp = requests.post(CHAT_API_URL, json=payload, timeout=600)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def read_file(path: str) -> str:
    abs_path = os.path.abspath(os.path.join(SAFE_WORKSPACE, path))
    if not abs_path.startswith(SAFE_WORKSPACE):
        raise ValueError("Acesso negado fora do workspace seguro.")
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_file(path: str, content: str):
    abs_path = os.path.abspath(os.path.join(SAFE_WORKSPACE, path))
    if not abs_path.startswith(SAFE_WORKSPACE):
        raise ValueError("Acesso negado fora do workspace seguro.")
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu-only", action="store_true", help="Executa pensando em ambiente sem GPU (apenas muda mensagens/logs)")
    args = parser.parse_args()

    print("=== Orquestrador AutoGen - Projeto Genesys ===")
    print(f"Workspace seguro: {SAFE_WORKSPACE}")
    print(f"API local do agente: {CHAT_API_URL}")

    # Exemplo simples de tarefa: pedir para o agente criar/atualizar um README dentro do workspace
    task_prompt = (
        "Crie um arquivo README_LOCAL.md explicando o objetivo do projeto, "
        "como rodar o backend FastAPI e como iniciar um ciclo de fine-tuning futuro. "
        "Se já existir, melhore o conteúdo. Retorne somente o texto final a ser salvo."
    )

    print("Chamando agente local...")
    result = call_local_agent(task_prompt)
    if "error" in result:
        print("Falha ao contatar agente:", result["error"])
        return

    content = result.get("response", "")
    if not content:
        print("Agente não retornou conteúdo válido.")
        return

    print("Aplicando mudança no workspace...")
    write_file("README_LOCAL.md", content)
    print("OK. Arquivo README_LOCAL.md atualizado.")

    # Loop de exemplo (poderia ser um round-robin entre múltiplos agentes)
    for _ in tqdm(range(3), desc="Ciclo de monitoramento"):
        time.sleep(1)

    print("Encerrando orquestrador básico.")


if __name__ == "__main__":
    main()


