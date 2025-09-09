# AgentMCP/agent_mcp/features/service_manager.py
import subprocess
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import psutil

from ..core import globals as g
from ..core.config import logger

# Armazenará a referência ao processo do Genesys Agent
g.genesys_process: Optional[subprocess.Popen] = None


def get_venv_python_path() -> str:
    """Determina o caminho para o executável Python dentro do .venv"""
    # Assumimos que o .venv está na raiz do projeto, um nível acima de 'AgentMCP'
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    venv_path = project_root / ".venv"

    if sys.platform == "win32":
        python_executable = venv_path / "Scripts" / "python.exe"
    else:
        python_executable = venv_path / "bin" / "python"

    if not python_executable.exists():
        logger.warning(
            f"Python executável não encontrado em '{python_executable}'. Usando o python do sistema."
        )
        return sys.executable

    return str(python_executable)


def start_genesys_process() -> Dict[str, Any]:
    """Inicia o servidor Genesys Agent como um subprocesso."""
    if g.genesys_process and g.genesys_process.poll() is None:
        return {
            "status": "already_running",
            "pid": g.genesys_process.pid,
            "message": "O processo do Genesys já está em execução.",
        }

    try:
        python_executable = get_venv_python_path()
        genesys_script_path = (
            Path(__file__).resolve().parent.parent.parent
            / "genesys_integration"
            / "genesys_server.py"
        )

        if not genesys_script_path.exists():
            logger.error(
                f"Script do servidor Genesys não encontrado em: {genesys_script_path}"
            )
            return {
                "status": "error",
                "message": "Script do servidor Genesys não encontrado.",
            }

        # No Windows, DETACHED_PROCESS cria um processo que não herda o console do pai.
        creationflags = subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0

        process = subprocess.Popen(
            [python_executable, str(genesys_script_path)],
            creationflags=creationflags,
            stdout=subprocess.PIPE,  # Redirecionar para logs posteriormente
            stderr=subprocess.PIPE,
        )
        g.genesys_process = process
        logger.info(f"Processo do Genesys iniciado com PID: {process.pid}")
        return {
            "status": "started",
            "pid": process.pid,
            "message": "Servidor Genesys iniciado com sucesso.",
        }
    except Exception as e:
        logger.error(f"Falha ao iniciar o processo do Genesys: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Falha ao iniciar o processo do Genesys: {e}",
        }


def stop_genesys_process() -> Dict[str, Any]:
    """Para o servidor Genesys Agent."""
    if not g.genesys_process or g.genesys_process.poll() is not None:
        return {
            "status": "not_running",
            "message": "O processo do Genesys não está em execução.",
        }

    try:
        pid = g.genesys_process.pid
        logger.info(f"Tentando parar o processo do Genesys com PID: {pid}")

        # Abordagem robusta para terminação em diferentes OS
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()

        g.genesys_process.wait(timeout=5)
        logger.info(f"Processo do Genesys com PID: {pid} parado com sucesso.")
        g.genesys_process = None
        return {
            "status": "stopped",
            "pid": pid,
            "message": "Servidor Genesys parado com sucesso.",
        }
    except psutil.NoSuchProcess:
        logger.warning(
            f"Processo do Genesys com PID {g.genesys_process.pid} não encontrado. Pode já ter sido finalizado."
        )
        g.genesys_process = None
        return {
            "status": "not_found",
            "message": "Processo não encontrado, possivelmente já finalizado.",
        }
    except Exception as e:
        logger.error(f"Erro ao parar o processo do Genesys: {e}", exc_info=True)
        # Tenta um kill como último recurso
        if g.genesys_process:
            g.genesys_process.kill()
            g.genesys_process = None
        return {
            "status": "error",
            "message": f"Erro ao parar processo: {e}. Forçado o encerramento.",
        }


def get_genesys_status() -> Dict[str, Any]:
    """Verifica o status do processo do Genesys Agent."""
    if g.genesys_process and g.genesys_process.poll() is None:
        try:
            p = psutil.Process(g.genesys_process.pid)
            return {
                "status": "running",
                "pid": g.genesys_process.pid,
                "cpu_percent": p.cpu_percent(interval=0.1),
                "memory_mb": p.memory_info().rss / (1024 * 1024),
            }
        except psutil.NoSuchProcess:
            g.genesys_process = None
            return {
                "status": "stopped",
                "pid": None,
                "message": "Processo não encontrado, estado interno corrigido.",
            }

    return {"status": "stopped", "pid": None}
