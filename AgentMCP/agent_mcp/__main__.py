#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ponto de entrada principal para executar o agent_mcp como um módulo.
Exemplo: python -m agent_mcp
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# --- Configuração de Caminho ---
# Garante que o diretório 'AgentMCP' esteja no path para que 'from agent_mcp.cli...' funcione
# quando executado com 'python -m agent_mcp' de dentro do diretório 'AgentMCP'.
# Esta lógica adapta o sys.path para permitir a execução como módulo.
if __name__ == "__main__" and __package__ is None:
    # Obtém o caminho do diretório onde __main__.py está localizado ('agent_mcp')
    main_dir = os.path.dirname(os.path.abspath(__file__))
    # Obtém o caminho do diretório pai ('AgentMCP')
    project_root = os.path.dirname(main_dir)
    # Adiciona o diretório pai ao sys.path para que 'agent_mcp' seja um pacote reconhecível
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from agent_mcp.cli import main_cli

# Load environment variables as the very first thing
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # Go up to Agent-MCP directory
env_file = project_root / ".env"

print(f"Looking for .env at: {env_file}")
if env_file.exists():
    print(f"Loading .env from: {env_file}")
    load_dotenv(dotenv_path=str(env_file))
    print(
        f"OPENAI_API_KEY in environment: {os.environ.get('OPENAI_API_KEY', 'NOT FOUND')[:20]}..."
    )
else:
    print(f"No .env file found at {env_file}")
    load_dotenv()  # Try default locations

# Agora importa e executa o CLI

if __name__ == "__main__":
    main_cli()
