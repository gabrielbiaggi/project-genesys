import subprocess
import psutil
from pathlib import Path
from typing import Dict, Any, Optional

from ...core.config import logger

# --- Configurações ---
PROJECT_ROOT = (
    Path(__file__).resolve().parents[4]
)  # Navega 4 níveis acima de features/dashboard/service_manager.py
LOG_DIR = PROJECT_ROOT / "logs"
BACKEND_PID_FILE = LOG_DIR / "backend.pid"
FRONTEND_PID_FILE = LOG_DIR / "frontend.pid"


def _get_pid_from_file(pid_file: Path) -> Optional[int]:
    """Lê um PID de um arquivo."""
    try:
        return int(pid_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def _is_process_running(pid: Optional[int], name_contains: str) -> bool:
    """Verifica se um processo com um determinado PID e nome está realmente rodando."""
    if pid is None:
        return False
    try:
        proc = psutil.Process(pid)
        # Verifica se o processo existe e se o nome do executável corresponde (flexível)
        return name_contains.lower() in proc.name().lower()
    except psutil.NoSuchProcess:
        return False
    except Exception as e:
        logger.error(f"Erro ao verificar processo {pid}: {e}")
        return False


def get_service_status() -> Dict[str, Any]:
    """Obtém o status de ambos os serviços (backend e frontend)."""
    backend_pid = _get_pid_from_file(BACKEND_PID_FILE)
    frontend_pid = _get_pid_from_file(FRONTEND_PID_FILE)

    backend_running = _is_process_running(backend_pid, "python")
    frontend_running = _is_process_running(
        frontend_pid, "node"
    )  # O processo principal é o Node.js

    # Limpar arquivos PID se os processos não estiverem mais rodando
    if not backend_running and BACKEND_PID_FILE.exists():
        BACKEND_PID_FILE.unlink()
    if not frontend_running and FRONTEND_PID_FILE.exists():
        FRONTEND_PID_FILE.unlink()

    return {
        "backend": {
            "status": "online" if backend_running else "offline",
            "pid": backend_pid if backend_running else None,
        },
        "frontend": {
            "status": "online" if frontend_running else "offline",
            "pid": frontend_pid if frontend_running else None,
        },
    }


def _run_script(script_name: str) -> Dict[str, Any]:
    """Função auxiliar para executar um script PowerShell do diretório raiz."""
    script_path = PROJECT_ROOT / script_name
    if not script_path.exists():
        return {"status": "error", "message": f"Script '{script_name}' não encontrado."}

    try:
        # Usar 'shell=True' pode ser necessário para scripts .ps1, dependendo do sistema
        # Para maior segurança, usamos a execução direta se possível
        result = subprocess.run(
            ["powershell.exe", "-File", str(script_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=PROJECT_ROOT,
        )
        logger.info(f"Saída do script '{script_name}': {result.stdout}")
        return {"status": "success", "message": result.stdout}
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar script '{script_name}': {e.stderr}")
        return {"status": "error", "message": e.stderr}
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Comando 'powershell.exe' não encontrado. Verifique se o PowerShell está no PATH.",
        }


def start_service(service_name: str) -> Dict[str, Any]:
    """Inicia um serviço específico (backend ou frontend) ou todos."""
    # Por simplicidade, vamos reutilizar o start.ps1 que já lida com ambos.
    # A lógica pode ser dividida no futuro, se necessário.
    logger.info(
        f"Tentando iniciar serviços via start.ps1 (requisitado por '{service_name}')..."
    )

    status_before = get_service_status()

    # Se ambos já estiverem online, não faz nada
    if (
        status_before["backend"]["status"] == "online"
        and status_before["frontend"]["status"] == "online"
    ):
        return {
            "status": "already_running",
            "message": "Todos os serviços já estão em execução.",
        }

    # Executa o script principal de inicialização
    result = _run_script("start.ps1")

    if result["status"] == "error":
        return result

    # Aguarda um pouco e verifica o novo status
    import time

    time.sleep(5)  # Dá tempo para os PIDs serem escritos
    status_after = get_service_status()

    return {
        "status": "success",
        "message": "Comando de inicialização executado.",
        "details": status_after,
        "script_output": result["message"],
    }


def stop_service(service_name: str) -> Dict[str, Any]:
    """Para um serviço específico (backend ou frontend) ou todos."""
    logger.info(
        f"Tentando parar serviços via stop.ps1 (requisitado por '{service_name}')..."
    )

    # Reutiliza o script stop.ps1 que já lida com a parada de ambos
    result = _run_script("stop.ps1")

    if result["status"] == "error":
        return result

    # Aguarda um pouco e verifica o novo status
    import time

    time.sleep(2)
    status_after = get_service_status()

    return {
        "status": "success",
        "message": "Comando de parada executado.",
        "details": status_after,
        "script_output": result["message"],
    }


def restart_service(service_name: str) -> Dict[str, Any]:
    """Reinicia todos os serviços."""
    logger.info(f"Reiniciando todos os serviços (requisitado por '{service_name}')...")
    stop_result = stop_service("all")
    if stop_result["status"] == "error":
        return {
            "status": "error",
            "message": "Falha ao parar os serviços durante o reinício.",
            "details": stop_result,
        }

    import time

    time.sleep(3)  # Pausa entre parar e iniciar

    start_result = start_service("all")
    if start_result["status"] == "error":
        return {
            "status": "error",
            "message": "Falha ao iniciar os serviços durante o reinício.",
            "details": start_result,
        }

    return {"status": "success", "message": "Serviços reiniciados."}
