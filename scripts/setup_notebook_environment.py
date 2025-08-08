#!/usr/bin/env python3
"""
scripts/setup_notebook_environment.py

Script simplificado para preparar o ambiente de teste do servidor Genesys.
Apenas instala dependências essenciais para teste remoto.

Uso:
    python scripts/setup_notebook_environment.py
    python scripts/setup_notebook_environment.py --upgrade
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from typing import List, Optional

# Dependências mínimas para teste remoto
TEST_REQUIREMENTS = [
    "requests",  # Para os scripts de teste
    "tqdm",      # Para barras de progresso  
]

class NotebookEnvironmentSetup:
    """Configurador do ambiente de notebook para testes do Genesys."""
    
    def __init__(self, force_reinstall: bool = False):
        self.force_reinstall = force_reinstall
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv-notebook"
        
        print("🔧 Configurador do Ambiente de Notebook - Projeto Genesys")
        print("=" * 60)
        print(f"📁 Diretório do projeto: {self.project_root}")
        print(f"🐍 Ambiente virtual: {self.venv_path}")
        print(f"🔄 Reinstalação forçada: {'Sim' if force_reinstall else 'Não'}")
        print("=" * 60)

    def check_python_version(self) -> bool:
        """Verifica se a versão do Python é adequada."""
        print("🐍 Verificando versão do Python...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python {version.major}.{version.minor} não suportado. Requer Python 3.8+")
            return False
        
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

    def create_virtual_environment(self) -> bool:
        """Cria o ambiente virtual se necessário."""
        if self.venv_path.exists() and not self.force_reinstall:
            print("📦 Ambiente virtual já existe - utilizando existente")
            return True
        
        if self.venv_path.exists() and self.force_reinstall:
            print("🗑️  Removendo ambiente virtual existente...")
            import shutil
            shutil.rmtree(self.venv_path)
        
        print("📦 Criando ambiente virtual...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True, text=True)
            
            print("✅ Ambiente virtual criado com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar ambiente virtual: {e}")
            print(f"Stderr: {e.stderr}")
            return False

    def get_pip_executable(self) -> Path:
        """Retorna o caminho para o executável pip do ambiente virtual."""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "pip.exe"
        else:  # Linux/Mac
            return self.venv_path / "bin" / "pip"

    def get_python_executable(self) -> Path:
        """Retorna o caminho para o executável Python do ambiente virtual."""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Linux/Mac
            return self.venv_path / "bin" / "python"

    def install_dependencies(self) -> bool:
        """Instala as dependências mínimas."""
        print("📥 Instalando dependências mínimas...")
        
        pip_exe = self.get_pip_executable()
        
        if not pip_exe.exists():
            print(f"❌ Pip não encontrado em: {pip_exe}")
            return False
        
        # Atualiza o pip primeiro
        print("⬆️  Atualizando pip...")
        try:
            subprocess.run([
                str(pip_exe), "install", "--upgrade", "pip"
            ], check=True, capture_output=True, text=True)
            print("✅ Pip atualizado")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Aviso: Não foi possível atualizar o pip: {e}")
        
        # Instala as dependências uma por uma para melhor controle
        failed_packages = []
        
        for package in NOTEBOOK_REQUIREMENTS:
            print(f"📦 Instalando {package}...")
            
            try:
                result = subprocess.run([
                    str(pip_exe), "install", package
                ], check=True, capture_output=True, text=True, timeout=300)
                
                print(f"✅ {package} instalado com sucesso")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao instalar {package}: {e}")
                print(f"Stderr: {e.stderr}")
                failed_packages.append(package)
                
            except subprocess.TimeoutExpired:
                print(f"⏱️  Timeout ao instalar {package}")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\n⚠️  Pacotes que falharam: {', '.join(failed_packages)}")
            print("💡 Tente executar novamente ou instalar manualmente")
            return False
        else:
            print("\n✅ Todas as dependências foram instaladas com sucesso!")
            return True

    def create_activation_script(self) -> bool:
        """Cria um script de ativação conveniente."""
        if os.name == 'nt':  # Windows
            script_content = f"""@echo off
echo 🚀 Ativando ambiente Genesys Notebook...
call "{self.venv_path}\\Scripts\\activate.bat"
echo ✅ Ambiente ativado! Use 'deactivate' para sair.
echo 💡 Execute: python scripts\\test_server_notebook.py
"""
            script_path = self.project_root / "activate_notebook.bat"
        else:  # Linux/Mac
            script_content = f"""#!/bin/bash
echo "🚀 Ativando ambiente Genesys Notebook..."
source "{self.venv_path}/bin/activate"
echo "✅ Ambiente ativado! Use 'deactivate' para sair."
echo "💡 Execute: python scripts/test_server_notebook.py"
"""
            script_path = self.project_root / "activate_notebook.sh"
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            if os.name != 'nt':
                os.chmod(script_path, 0o755)  # Torna executável no Linux/Mac
            
            print(f"📝 Script de ativação criado: {script_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar script de ativação: {e}")
            return False

    def create_env_file_template(self) -> bool:
        """Cria um template do arquivo .env se não existir."""
        env_path = self.project_root / ".env"
        
        if env_path.exists():
            print("📄 Arquivo .env já existe - mantendo configuração atual")
            return True
        
        env_template = """# Configuração do Projeto Genesys - Modo Notebook
# Este arquivo é para testes básicos no notebook

# === URL DO SERVIDOR (Cloudflare Tunnel) ===
# Substitua pela URL do seu túnel Cloudflare quando disponível
SERVER_URL=http://localhost:8002

# === CONFIGURAÇÕES BÁSICAS ===
API_HOST=0.0.0.0
API_PORT=8002

# === CONFIGURAÇÕES DE MODELO (Para referência) ===
# Essas configurações são usadas no servidor principal, não no notebook
HUGGING_FACE_REPO_ID=meta-llama/Meta-Llama-3-8B-Instruct
MODEL_GGUF_FILENAME=Meta-Llama-3-8B-Instruct-Q4_K_M.gguf
MULTIMODAL_PROJECTOR_FILENAME=

# === TOKENS DE API (Opcionais para testes) ===
# HUGGING_FACE_HUB_TOKEN=seu_token_aqui
# CLOUDFLARE_TUNNEL_TOKEN=seu_token_aqui
"""
        
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_template)
            
            print(f"📄 Template .env criado: {env_path}")
            print("💡 Edite o arquivo .env para configurar URLs e tokens")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar template .env: {e}")
            return False

    def verify_installation(self) -> bool:
        """Verifica se a instalação foi bem-sucedida."""
        print("\n🔍 Verificando instalação...")
        
        python_exe = self.get_python_executable()
        
        if not python_exe.exists():
            print(f"❌ Python não encontrado em: {python_exe}")
            return False
        
        # Testa as importações principais
        test_imports = [
            "fastapi",
            "uvicorn",
            "dotenv",
            "requests"
        ]
        
        for module in test_imports:
            try:
                result = subprocess.run([
                    str(python_exe), "-c", f"import {module}; print(f'✅ {module} OK')"
                ], check=True, capture_output=True, text=True, timeout=10)
                
                print(result.stdout.strip())
                
            except subprocess.CalledProcessError:
                print(f"❌ Falha ao importar {module}")
                return False
            except subprocess.TimeoutExpired:
                print(f"⏱️  Timeout ao testar {module}")
                return False
        
        print("✅ Verificação concluída - ambiente pronto!")
        return True

    def setup_complete_environment(self) -> bool:
        """Executa a configuração completa do ambiente."""
        print("🚀 Iniciando configuração completa do ambiente de notebook...\n")
        
        # Sequência de configuração
        steps = [
            ("Verificação do Python", self.check_python_version),
            ("Criação do ambiente virtual", self.create_virtual_environment),
            ("Instalação de dependências", self.install_dependencies),
            ("Criação do script de ativação", self.create_activation_script),
            ("Criação do template .env", self.create_env_file_template),
            ("Verificação da instalação", self.verify_installation),
        ]
        
        for step_name, step_function in steps:
            print(f"\n📋 {step_name}...")
            print("-" * 40)
            
            if not step_function():
                print(f"\n❌ FALHA na etapa: {step_name}")
                print("🛑 Configuração interrompida")
                return False
            
            print(f"✅ {step_name} concluída")
        
        # Sucesso!
        print("\n" + "=" * 60)
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Ative o ambiente:")
        
        if os.name == 'nt':
            print("   > activate_notebook.bat")
        else:
            print("   $ source activate_notebook.sh")
        
        print("\n2. Configure a URL do servidor no arquivo .env")
        print("\n3. Execute os testes:")
        print("   python scripts/test_server_notebook.py")
        print("\n4. Para testes rápidos:")
        print("   python scripts/test_server_notebook.py --quick")
        print("\n🚀 Ambiente pronto para testar o servidor Genesys!")
        
        return True

def main():
    """Função principal do script de configuração."""
    parser = argparse.ArgumentParser(
        description="Configura o ambiente mínimo no notebook para testar o servidor Genesys"
    )
    
    parser.add_argument(
        "--force-reinstall",
        action="store_true",
        help="Força a reinstalação do ambiente virtual"
    )
    
    args = parser.parse_args()
    
    # Executa a configuração
    setup = NotebookEnvironmentSetup(force_reinstall=args.force_reinstall)
    
    try:
        success = setup.setup_complete_environment()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuração interrompida pelo usuário")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n❌ Erro inesperado durante a configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
