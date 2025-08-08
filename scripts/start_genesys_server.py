#!/usr/bin/env python3
"""
scripts/start_genesys_server.py

Script completo para inicializar o servidor Genesys com todos os componentes.
Este script automatiza todo o processo de startup da IA no servidor.

Uso:
    python scripts/start_genesys_server.py
    python scripts/start_genesys_server.py --port 8002
    python scripts/start_genesys_server.py --model-check-only
"""

import os
import sys
import time
import subprocess
import argparse
import signal
from pathlib import Path
from typing import Optional, List
import psutil

class GenesysServerManager:
    """Gerenciador completo do servidor Genesys."""
    
    def __init__(self, port: int = 8002, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        self.python_exe = self._get_python_executable()
        self.server_process = None
        
        print("🤖 Genesys Server Manager")
        print("=" * 60)
        print(f"📁 Projeto: {self.project_root}")
        print(f"🐍 Python: {self.python_exe}")
        print(f"🌐 Servidor: {self.host}:{self.port}")
        print("=" * 60)

    def _get_python_executable(self) -> Path:
        """Retorna o caminho para o Python do ambiente virtual."""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Linux/Mac
            return self.venv_path / "bin" / "python"

    def check_environment(self) -> bool:
        """Verifica se o ambiente está configurado corretamente."""
        print("🔍 Verificando ambiente...")
        
        # Verifica se o Python existe
        if not self.python_exe.exists():
            print(f"❌ Python não encontrado: {self.python_exe}")
            print("💡 Execute: python -m venv venv && venv\\Scripts\\activate && pip install -r requirements.txt")
            return False
        
        print(f"✅ Python encontrado: {self.python_exe}")
        
        # Verifica dependências essenciais
        essential_modules = ["fastapi", "uvicorn", "langchain", "llama_cpp"]
        
        for module in essential_modules:
            try:
                result = subprocess.run([
                    str(self.python_exe), "-c", f"import {module.replace('-', '_')}"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"✅ {module} - OK")
                else:
                    print(f"❌ {module} - FALTANDO")
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️  {module} - TIMEOUT")
                return False
            except Exception as e:
                print(f"❌ {module} - ERRO: {e}")
                return False
        
        return True

    def check_model_files(self) -> bool:
        """Verifica se os arquivos do modelo estão disponíveis."""
        print("\n📥 Verificando arquivos do modelo...")
        
        models_dir = self.project_root / "models"
        
        if not models_dir.exists():
            print(f"❌ Diretório de modelos não encontrado: {models_dir}")
            print("💡 Execute o script de download primeiro")
            return False
        
        # Procura por arquivos GGUF
        gguf_files = list(models_dir.glob("*.gguf"))
        
        if not gguf_files:
            print("❌ Nenhum arquivo de modelo (.gguf) encontrado")
            print("💡 Execute: python scripts/download_model.py")
            return False
        
        for model_file in gguf_files:
            size_gb = model_file.stat().st_size / (1024**3)
            print(f"✅ Modelo: {model_file.name} ({size_gb:.1f} GB)")
        
        return True

    def download_model_if_needed(self) -> bool:
        """Baixa o modelo se não estiver disponível."""
        if self.check_model_files():
            return True
        
        print("\n📥 Modelo não encontrado. Iniciando download...")
        
        try:
            download_script = self.project_root / "scripts" / "download_model.py"
            
            if not download_script.exists():
                print(f"❌ Script de download não encontrado: {download_script}")
                return False
            
            print("🔄 Executando download do modelo...")
            result = subprocess.run([
                str(self.python_exe), str(download_script)
            ], cwd=self.project_root, timeout=3600)  # 1 hora de timeout
            
            if result.returncode == 0:
                print("✅ Download concluído com sucesso")
                return self.check_model_files()
            else:
                print(f"❌ Download falhou com código: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout no download do modelo")
            return False
        except Exception as e:
            print(f"❌ Erro durante o download: {e}")
            return False

    def check_port_availability(self) -> bool:
        """Verifica se a porta está disponível."""
        print(f"\n🔌 Verificando disponibilidade da porta {self.port}...")
        
        for conn in psutil.net_connections():
            if conn.laddr.port == self.port:
                print(f"❌ Porta {self.port} já está em uso")
                print(f"📋 Processo: PID {conn.pid}")
                return False
        
        print(f"✅ Porta {self.port} disponível")
        return True

    def start_server(self) -> bool:
        """Inicia o servidor Genesys."""
        print(f"\n🚀 Iniciando servidor Genesys...")
        
        # Comando para iniciar o servidor
        cmd = [
            str(self.python_exe), "-m", "uvicorn", 
            "app.main:app",
            "--host", self.host,
            "--port", str(self.port),
            "--reload"
        ]
        
        try:
            print(f"📋 Comando: {' '.join(cmd)}")
            print("🔄 Iniciando servidor...")
            
            # Inicia o processo
            self.server_process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Aguarda alguns segundos para o servidor inicializar
            print("⏱️  Aguardando inicialização...")
            time.sleep(5)
            
            # Verifica se o processo ainda está rodando
            if self.server_process.poll() is None:
                print(f"✅ Servidor iniciado com sucesso!")
                print(f"🌐 Acesso local: http://localhost:{self.port}")
                print(f"🌍 Acesso túnel: https://genesys.webcreations.com.br")
                return True
            else:
                print("❌ Servidor falhou ao iniciar")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            return False

    def monitor_server(self):
        """Monitora o servidor e exibe os logs."""
        if not self.server_process:
            print("❌ Nenhum servidor rodando para monitorar")
            return
        
        print("\n📊 Monitorando servidor... (Ctrl+C para parar)")
        print("=" * 60)
        
        try:
            # Lê e exibe os logs do servidor
            for line in iter(self.server_process.stdout.readline, ''):
                if line:
                    print(line.strip())
                
                # Verifica se o processo ainda está rodando
                if self.server_process.poll() is not None:
                    print("\n⚠️  Servidor parou inesperadamente")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupção solicitada pelo usuário")
            self.stop_server()

    def stop_server(self):
        """Para o servidor Genesys."""
        if self.server_process and self.server_process.poll() is None:
            print("\n🛑 Parando servidor...")
            
            try:
                # Tenta parar graciosamente
                self.server_process.terminate()
                
                # Aguarda até 10 segundos
                try:
                    self.server_process.wait(timeout=10)
                    print("✅ Servidor parado graciosamente")
                except subprocess.TimeoutExpired:
                    # Força a parada se necessário
                    print("🔨 Forçando parada do servidor...")
                    self.server_process.kill()
                    self.server_process.wait()
                    print("✅ Servidor forçado a parar")
                    
            except Exception as e:
                print(f"❌ Erro ao parar servidor: {e}")
        else:
            print("ℹ️  Nenhum servidor rodando")

    def run_full_startup(self) -> bool:
        """Executa o processo completo de startup."""
        print("🚀 Iniciando processo completo de startup do Genesys...")
        print("=" * 60)
        
        # Sequência de verificações e inicialização
        steps = [
            ("Verificação do ambiente", self.check_environment),
            ("Verificação da porta", self.check_port_availability),
            ("Download do modelo (se necessário)", self.download_model_if_needed),
            ("Inicialização do servidor", self.start_server),
        ]
        
        for step_name, step_function in steps:
            print(f"\n📋 {step_name}...")
            print("-" * 40)
            
            if not step_function():
                print(f"\n❌ FALHA na etapa: {step_name}")
                print("🛑 Startup interrompido")
                return False
            
            print(f"✅ {step_name} - OK")
        
        print("\n" + "=" * 60)
        print("🎉 GENESYS SERVIDOR INICIADO COM SUCESSO!")
        print("=" * 60)
        print(f"🌐 URL Local: http://localhost:{self.port}")
        print(f"🌍 URL Túnel: https://genesys.webcreations.com.br")
        print(f"📚 Documentação: http://localhost:{self.port}/docs")
        print("\n💡 Para testar:")
        print("python scripts/test_server_notebook.py --server-url https://genesys.webcreations.com.br")
        print("\n🛑 Pressione Ctrl+C para parar o servidor")
        
        return True

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Inicia o servidor Genesys com todos os componentes"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8002,
        help="Porta do servidor (padrão: 8002)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host do servidor (padrão: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--model-check-only",
        action="store_true",
        help="Apenas verifica os modelos sem iniciar o servidor"
    )
    
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Não tenta baixar o modelo automaticamente"
    )
    
    args = parser.parse_args()
    
    # Cria o gerenciador
    manager = GenesysServerManager(port=args.port, host=args.host)
    
    # Configura tratamento de sinais para parada limpa
    def signal_handler(signum, frame):
        print("\n🛑 Sinal de interrupção recebido")
        manager.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.model_check_only:
            # Apenas verifica os modelos
            print("🔍 Verificando apenas os modelos...")
            success = manager.check_model_files()
            sys.exit(0 if success else 1)
        
        # Executa startup completo
        if manager.run_full_startup():
            # Monitora o servidor
            manager.monitor_server()
        else:
            print("\n❌ Falha no startup do servidor")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Startup interrompido pelo usuário")
        manager.stop_server()
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        manager.stop_server()
        sys.exit(1)

if __name__ == "__main__":
    main()
