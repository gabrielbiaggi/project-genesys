#!/usr/bin/env python3
"""
Agent-MCP CLI: Command-line interface for multi-agent collaboration.

Copyright (C) 2025 Luis Alejandro Rincon (rinadelph)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
from pathlib import Path
import json
import sqlite3
from typing import Optional

import click
from agent_mcp.core.config import logger

# --- Configuração Inicial do Ambiente ---
# Adiciona o diretório pai (AgentMCP) ao sys.path para permitir importações relativas
# como `from agent_mcp.core...` antes mesmo de o pacote ser instalado.
# Isso é crucial para rodar o CLI diretamente do código-fonte.
project_root = Path(__file__).resolve().parents[2]  # Sobe dois níveis para a raiz do projeto (Genesys)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# --- Configuração de Caminho e Variáveis de Ambiente ---
# É CRÍTICO definir a variável de ambiente MCP_PROJECT_DIR *antes* de importar
# qualquer outro módulo do projeto, pois o logger e outras configurações dependem dela.
# O valor padrão é o diretório atual, mas será sobrescrito pela opção --project-dir.
os.environ.setdefault("MCP_PROJECT_DIR", os.path.abspath("."))


# --- Importações do Projeto (depois da configuração do ambiente) ---
# from .core.config import (
#     logger,
# )  # Logger is initialized in config.py

# Import app creation and lifecycle functions
# TUI foi removido, não é necessário para a operação em modo de serviço
# from .tui.display import TUIDisplay


def get_admin_token_from_db(project_dir: str) -> Optional[str]:
    """Get the admin token from the SQLite database."""
    try:
        # Construct the path to the database
        db_path = Path(project_dir).resolve() / ".agent" / "mcp_state.db"

        if not db_path.exists():
            return None

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get the admin token from project_context table
        cursor.execute(
            "SELECT value FROM project_context WHERE context_key = ?",
            ("config_admin_token",),
        )
        row = cursor.fetchone()

        if row and row["value"]:
            try:
                admin_token = json.loads(row["value"])
                if isinstance(admin_token, str) and admin_token:
                    return admin_token
            except json.JSONDecodeError:
                pass

        conn.close()
        return None
    except Exception as e:
        logger.error(f"Error reading admin token from database: {e}")
        return None


# --- Click Command Definition ---
# This replicates the @click.command and options from the original main.py (lines 1936-1950)
@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--port",
    type=int,
    default=os.environ.get("PORT", 8080),  # Read from env var PORT if set, else 8080
    show_default=True,
    help="Port to listen on for SSE and HTTP dashboard.",
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"], case_sensitive=False),
    default="sse",
    show_default=True,
    help="Transport type for MCP communication (stdio or sse).",
)
@click.option(
    "--project-dir",
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True, writable=True),
    default=".",
    show_default=True,
    help="Project directory. The .agent folder will be created/used here. Defaults to current directory.",
)
@click.option(
    "--admin-token",  # Renamed from admin_token_param for clarity
    "admin_token_cli",  # Variable name for the parameter
    type=str,
    default=None,
    help="Admin token for authentication. If not provided, one will be loaded from DB or generated.",
)
@click.option(
    "--debug",
    is_flag=True,
    default=os.environ.get("MCP_DEBUG", "false").lower()
    == "true",  # Default from env var
    help="Enable debug mode for the server (more verbose logging, Starlette debug pages).",
)
@click.option(
    "--no-tui",
    is_flag=True,
    default=False,
    help="Disable the terminal UI display (logs will still go to file).",
)
@click.option(
    "--advanced",
    is_flag=True,
    default=False,
    help="Enable advanced embeddings mode with larger dimension (3072) and more sophisticated code analysis.",
)
@click.option(
    "--git",
    is_flag=True,
    default=False,
    help="Enable experimental Git worktree support for parallel agent development (advanced users only).",
)
@click.option(
    "--no-index",
    is_flag=True,
    default=False,
    help="Disable automatic markdown file indexing. Allows selective manual indexing of specific content into the RAG system.",
)
def main_cli(
    port: int,
    transport: str,
    project_dir: str,
    admin_token_cli: Optional[str],
    debug: bool,
    no_tui: bool,
    advanced: bool,
    git: bool,
    no_index: bool,
):
    """Main entry point for the MCP server CLI."""
    # --- Set Environment Variables from CLI options ---
    # O MCP_PROJECT_DIR é a primeira e mais importante variável a ser definida.
    os.environ["MCP_PROJECT_DIR"] = project_dir

    # We can pass other CLI flags via environment variables if needed
    os.environ["MCP_DEBUG"] = "true" if debug else "false"
    os.environ["MCP_ADVANCED_EMBEDDINGS"] = "true" if advanced else "false"
    os.environ["MCP_GIT_WORKTREES"] = "true" if git else "false"
    os.environ["MCP_DISABLE_AUTO_INDEXING"] = "true" if no_index else "false"

    # Store the admin token from the CLI in a temporary global or env var
    # so `application_startup` can access it.
    if admin_token_cli:
        os.environ["MCP_ADMIN_TOKEN_CLI"] = admin_token_cli

    # O resto da lógica da main_cli original permanece,
    # mas a execução real do servidor agora será tratada pelo Uvicorn.
    # Mantemos a lógica de configuração aqui para garantir que ela seja executada antes do início do Uvicorn.

    logger.info("Starting Agent-MCP Server...")
    logger.info(f"Transport: {transport}, Port: {port}")
    logger.info(f"Project Directory: {project_dir}")

    # A fábrica `create_app` em `main_app.py` agora lerá essas variáveis de ambiente.
    # Não precisamos mais chamar application_startup aqui porque o
    # evento `on_startup` do Starlette o acionará.

    if transport == "sse":
        # Use uvicorn to run the app defined by the factory `create_app`
        # This is the standard way to run a Starlette/FastAPI app.
        import uvicorn

        uvicorn.run(
            "agent_mcp.app.main_app:create_app",
            host="0.0.0.0",
            port=port,
            factory=True,  # Tells uvicorn that the string is a factory function
            reload=debug,  # Enable auto-reload in debug mode
        )
    elif transport == "stdio":
        # A lógica stdio foi removida pois não é relevante para a execução como serviço.
        logger.error("Transport 'stdio' is no longer supported for service mode.")
        sys.exit(1)


# A função main_async_stdio foi removida pois não é mais necessária.

# This allows running `python -m mcp_server_src.cli --port ...`
if __name__ == "__main__":
    main_cli()
