#!/usr/bin/env python3
# scripts/genesys_service_runner.py
# Script runner otimizado para execução como serviço Windows

import sys
import os
import logging
import signal
import argparse
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager

# Adicionar raiz do projeto ao Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configuração de logging para serviço
def setup_service_logging():
    """Configura logging específico para serviço Windows"""
    logs_dir = Path(project_root) / "data" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / "genesys_service.log"
    
    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configurar loggers específicos
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

# Configurar signal handlers para shutdown graceful
class ServiceManager:
    def __init__(self):
        self.logger = setup_service_logging()
        self.server = None
        self.shutdown_requested = False
        
    def setup_signal_handlers(self):
        """Configura handlers para shutdown graceful"""
        def signal_handler(signum, frame):
            self.logger.info(f"Recebido sinal {signum}. Iniciando shutdown graceful...")
            self.shutdown_requested = True
            if self.server:
                self.server.should_exit = True
        
        # Windows signals
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Windows-specific
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, signal_handler)
            
    def run_server(self, host: str = "0.0.0.0", port: int = 8002):
        """Executa o servidor Genesys"""
        self.logger.info("🚀 Iniciando Genesys AI Server como serviço Windows...")
        self.logger.info(f"📍 Host: {host}, Porta: {port}")
        self.logger.info(f"📂 Diretório do projeto: {project_root}")
        
        try:
            # Verificar se app está disponível
            try:
                from app.main import app
                self.logger.info("✅ Aplicação FastAPI carregada com sucesso")
            except ImportError as e:
                self.logger.error(f"❌ Erro ao importar aplicação: {e}")
                return 1
            except Exception as e:
                self.logger.error(f"❌ Erro inesperado ao carregar aplicação: {e}")
                return 1
            
            # Configuração do Uvicorn para serviço
            config = uvicorn.Config(
                app="app.main:app",
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                reload=False,  # Nunca usar reload em serviço
                workers=1,     # Single worker para evitar problemas
                loop="asyncio",
                app_dir=project_root,
                # Configurações específicas para Windows Service
                use_colors=False,  # Sem cores nos logs
                log_config={
                    "version": 1,
                    "disable_existing_loggers": False,
                    "formatters": {
                        "default": {
                            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        },
                    },
                    "handlers": {
                        "default": {
                            "formatter": "default",
                            "class": "logging.StreamHandler",
                            "stream": "ext://sys.stdout",
                        },
                        "file": {
                            "formatter": "default", 
                            "class": "logging.FileHandler",
                            "filename": str(Path(project_root) / "data" / "logs" / "uvicorn_service.log"),
                            "encoding": "utf-8",
                        },
                    },
                    "root": {
                        "level": "INFO",
                        "handlers": ["default", "file"],
                    },
                }
            )
            
            # Criar servidor
            self.server = uvicorn.Server(config)
            self.logger.info("🔧 Servidor Uvicorn configurado")
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Executar servidor
            self.logger.info("🎯 Iniciando servidor...")
            self.server.run()
            
            self.logger.info("✅ Servidor finalizado normalmente")
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Interrupção pelo usuário")
            return 0
        except Exception as e:
            self.logger.error(f"❌ Erro crítico no serviço: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return 1
        finally:
            self.logger.info("🏁 Serviço Genesys finalizado")

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    logger = logging.getLogger(__name__)
    
    # Verificar se está no diretório correto
    app_main_path = Path(project_root) / "app" / "main.py"
    if not app_main_path.exists():
        logger.error(f"❌ Arquivo app/main.py não encontrado em: {project_root}")
        return False
    
    # Verificar Python path
    logger.info(f"🐍 Python executable: {sys.executable}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"📍 Project root: {project_root}")
    logger.info(f"🔗 Python path: {sys.path[:3]}...")  # Mostrar primeiros 3
    
    return True

def main():
    """Função principal do serviço"""
    parser = argparse.ArgumentParser(description="Genesys AI Service Runner")
    parser.add_argument("--host", default="0.0.0.0", help="Host para bind do servidor")
    parser.add_argument("--port", type=int, default=8002, help="Porta para o servidor")
    parser.add_argument("--check", action="store_true", help="Apenas verificar ambiente")
    
    args = parser.parse_args()
    
    # Setup inicial do logging
    logger = setup_service_logging()
    
    logger.info("=" * 60)
    logger.info("🤖 GENESYS AI SERVICE RUNNER")
    logger.info("=" * 60)
    logger.info(f"🎯 Argumentos: host={args.host}, port={args.port}")
    
    # Verificar ambiente
    if not check_environment():
        logger.error("❌ Falha na verificação do ambiente")
        return 1
    
    if args.check:
        logger.info("✅ Verificação do ambiente concluída com sucesso")
        return 0
    
    # Executar serviço
    service_manager = ServiceManager()
    return service_manager.run_server(args.host, args.port)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
