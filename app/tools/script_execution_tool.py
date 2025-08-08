# app/tools/script_execution_tool.py
import os
import subprocess
from langchain.tools import tool

@tool("ExecutePythonScript")
def execute_python_script(script_path: str) -> str:
    """
    Executa um script Python especificado usando o mesmo ambiente virtual do servidor.
    O caminho do script deve ser relativo à raiz do projeto.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    absolute_script_path = os.path.join(project_root, script_path)

    if not os.path.exists(absolute_script_path):
        return f"Erro: O script '{script_path}' não foi encontrado."

    # Constrói o caminho para o executável Python dentro do venv
    python_executable = os.path.join(project_root, 'venv', 'Scripts', 'python.exe')

    try:
        print(f"Executando o script: {absolute_script_path}")
        result = subprocess.run(
            [python_executable, absolute_script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root
        )
        output = f"Script '{script_path}' executado com sucesso.\n"
        output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"
        return output
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o script '{script_path}'.\nExit Code: {e.returncode}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
    except Exception as e:
        return f"Uma exceção inesperada ocorreu: {e}"
