# app/tools/terminal_tool.py
from langchain.tools import tool
import subprocess
import os

# Usamos o mesmo workspace seguro da ferramenta de arquivos
SAFE_WORKSPACE = os.path.join(os.path.dirname(__file__), '..', '..', 'workspace')

@tool("ExecuteTerminalCommand")
def execute_terminal_command(command: str) -> str:
    """
    Executa um comando de terminal no diretório de trabalho seguro.
    Use com extrema cautela. Apenas comandos seguros são permitidos.
    Comandos perigosos como 'rm -rf /' são bloqueados.
    """
    # Medida de segurança básica para prevenir comandos destrutivos óbvios
    if "rm -rf" in command and ("/" in command.split("rm -rf")[1].strip() or ".." in command):
        return "Erro de Segurança: Comando 'rm -rf' com escopo amplo é estritamente proibido."

    try:
        # Executa o comando dentro do workspace seguro
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            cwd=SAFE_WORKSPACE
        )
        output = f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"
        return output
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar comando '{command}'.\nExit Code: {e.returncode}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
    except Exception as e:
        return f"Uma exceção inesperada ocorreu: {e}"

