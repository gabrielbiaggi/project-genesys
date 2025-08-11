#!/usr/bin/env python3
# setup_notebook_treinamento.py
# Setup rápido para notebook - Sistema de Treinamento Genesys

"""
🚀 SETUP RÁPIDO - SISTEMA DE TREINAMENTO GENESYS

Este script configura rapidamente o ambiente de notebook para:
- Monitorar o sistema Genesys remotamente
- Controlar treinamento da IA
- Visualizar métricas e performance
- Executar análises de dados

USO:
    # Em notebook/terminal
    python setup_notebook_treinamento.py
    
    # Ou importar diretamente
    from setup_notebook_treinamento import *
"""

import sys
import subprocess
import importlib
from pathlib import Path
import requests
import json

# Configurações
GENESYS_SERVER = "https://genesys.webcreations.com.br"
REQUIRED_PACKAGES = [
    "requests",
    "pandas", 
    "numpy",
    "matplotlib",
    "seaborn",
    "tqdm"
]

class NotebookTrainingSetup:
    """Configurador do ambiente de treinamento para notebook"""
    
    def __init__(self):
        self.server_url = GENESYS_SERVER
        print("🤖 CONFIGURANDO AMBIENTE DE TREINAMENTO GENESYS")
        print("=" * 55)
    
    def check_dependencies(self) -> bool:
        """Verifica e instala dependências necessárias"""
        print("📦 Verificando dependências...")
        
        missing_packages = []
        for package in REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package} - FALTANDO")
        
        if missing_packages:
            print(f"\n📥 Instalando pacotes faltantes: {', '.join(missing_packages)}")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "--quiet", "--user", *missing_packages
                ])
                print("✅ Dependências instaladas com sucesso!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao instalar dependências: {e}")
                return False
        else:
            print("✅ Todas as dependências estão disponíveis!")
            return True
    
    def test_server_connection(self) -> bool:
        """Testa conexão com servidor Genesys"""
        print("\n🌐 Testando conexão com servidor...")
        
        try:
            response = requests.get(f"{self.server_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Servidor online: {self.server_url}")
                print(f"  📊 Status: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"  ❌ Erro HTTP: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Falha na conexão: {e}")
            return False
    
    def test_training_endpoints(self) -> bool:
        """Testa endpoints específicos de treinamento"""
        print("\n🧪 Testando endpoints de treinamento...")
        
        # Testar endpoint Continue (para validar API)
        try:
            test_payload = {
                "model": "genesys-local",
                "messages": [{"role": "user", "content": "teste de conectividade"}]
            }
            
            response = requests.post(
                f"{self.server_url}/v1/chat/completions",
                json=test_payload,
                headers={"Authorization": "Bearer dummy"},
                timeout=10
            )
            
            if response.status_code == 200:
                print("  ✅ API Continue funcionando")
                return True
            else:
                print(f"  ⚠️ API Continue retornou: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Erro ao testar endpoints: {e}")
            return False
    
    def create_data_directories(self):
        """Cria estrutura de diretórios para dados"""
        print("\n📁 Criando estrutura de diretórios...")
        
        directories = [
            "data/logs",
            "data/raw",
            "data/processed", 
            "data/training",
            "data/metrics",
            "notebooks"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"  📂 {dir_path}")
        
        print("✅ Estrutura de diretórios criada!")
    
    def create_example_notebook(self):
        """Cria notebook de exemplo para treinamento"""
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# 🤖 Sistema de Treinamento Genesys\n",
                        "\n",
                        "Este notebook demonstra como usar o sistema de treinamento remoto.\n",
                        "\n",
                        "## 🚀 Início Rápido"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Importar sistema de monitoramento\n",
                        "import sys\n",
                        "sys.path.append('scripts')\n",
                        "\n",
                        "from monitor_treinamento_notebook import GenesysTrainingMonitor\n",
                        "\n",
                        "# Criar monitor\n",
                        "monitor = GenesysTrainingMonitor()\n",
                        "print(\"✅ Sistema de treinamento carregado!\")"
                    ]
                },
                {
                    "cell_type": "code", 
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Verificar status do servidor\n",
                        "status = monitor.check_server_status()\n",
                        "print(f\"Status do servidor: {status}\")"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None, 
                    "metadata": {},
                    "source": [
                        "# Ver estatísticas de interação\n",
                        "stats = monitor.get_interaction_stats()\n",
                        "print(f\"Estatísticas: {stats}\")"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Dashboard visual de performance\n",
                        "monitor.plot_performance_dashboard()"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Iniciar treinamento monitorado\n",
                        "# CUIDADO: Isso irá disparar treinamento real!\n",
                        "# monitor.start_training_with_monitoring()"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        notebook_path = Path("notebooks/treinamento_genesys_exemplo.ipynb")
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook_content, f, indent=2, ensure_ascii=False)
        
        print(f"📓 Notebook de exemplo criado: {notebook_path}")
    
    def generate_quick_commands(self):
        """Gera comandos rápidos para uso"""
        commands = """
# 🚀 COMANDOS RÁPIDOS PARA NOTEBOOK

## Importar sistema de treinamento:
```python
import sys
sys.path.append('scripts')
from monitor_treinamento_notebook import GenesysTrainingMonitor
monitor = GenesysTrainingMonitor()
```

## Verificar servidor:
```python
status = monitor.check_server_status()
print(status)
```

## Ver estatísticas:
```python
stats = monitor.get_interaction_stats()
print(stats)
```

## Dashboard visual:
```python
monitor.plot_performance_dashboard()
```

## Iniciar treinamento:
```python
monitor.start_training_with_monitoring()
```

## Sistema AutoGen completo:
```python
from sistema_treinamento_autogen import AutoGenTrainingSystem
training = AutoGenTrainingSystem()
results = await training.run_training_cycle()
```
"""
        
        with open("COMANDOS_RAPIDOS_NOTEBOOK.md", 'w', encoding='utf-8') as f:
            f.write(commands)
        
        print("📋 Arquivo de comandos rápidos criado: COMANDOS_RAPIDOS_NOTEBOOK.md")
    
    def run_setup(self) -> bool:
        """Executa setup completo"""
        try:
            # 1. Verificar dependências
            if not self.check_dependencies():
                print("❌ Falha ao configurar dependências")
                return False
            
            # 2. Testar servidor
            if not self.test_server_connection():
                print("⚠️ Servidor não acessível - modo offline")
            
            # 3. Testar endpoints
            self.test_training_endpoints()
            
            # 4. Criar estrutura
            self.create_data_directories()
            
            # 5. Criar exemplo
            self.create_example_notebook()
            
            # 6. Gerar comandos
            self.generate_quick_commands()
            
            print("\n" + "=" * 55)
            print("✅ SETUP CONCLUÍDO COM SUCESSO!")
            print("=" * 55)
            print("📓 Abra: notebooks/treinamento_genesys_exemplo.ipynb")
            print("📋 Consulte: COMANDOS_RAPIDOS_NOTEBOOK.md")
            print("🚀 Sistema pronto para uso!")
            print("=" * 55)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante setup: {e}")
            return False

# Funções de conveniência para import direto
def setup_genesys_training():
    """Função de conveniência para setup rápido"""
    setup = NotebookTrainingSetup()
    return setup.run_setup()

def get_monitor():
    """Função de conveniência para obter monitor"""
    try:
        sys.path.append('scripts')
        from monitor_treinamento_notebook import GenesysTrainingMonitor
        return GenesysTrainingMonitor()
    except Exception as e:
        print(f"❌ Erro ao carregar monitor: {e}")
        return None

def get_training_system():
    """Função de conveniência para obter sistema de treinamento"""
    try:
        sys.path.append('scripts')
        from sistema_treinamento_autogen import AutoGenTrainingSystem
        return AutoGenTrainingSystem()
    except Exception as e:
        print(f"❌ Erro ao carregar sistema de treinamento: {e}")
        return None

# Para uso em notebook - variáveis globais convenientes
monitor = None
training_system = None

def init_genesys():
    """Inicialização rápida para notebook"""
    global monitor, training_system
    
    print("🤖 Inicializando Sistema Genesys para Notebook...")
    
    try:
        monitor = get_monitor()
        training_system = get_training_system()
        
        if monitor:
            print("✅ Monitor carregado: use 'monitor'")
        if training_system:
            print("✅ Sistema de treinamento carregado: use 'training_system'")
        
        print("\n🎯 Comandos disponíveis:")
        print("  - monitor.check_server_status()")
        print("  - monitor.get_interaction_stats()") 
        print("  - monitor.plot_performance_dashboard()")
        print("  - monitor.start_training_with_monitoring()")
        print("\n🚀 Sistema pronto!")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")

def main():
    """Função principal"""
    setup = NotebookTrainingSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎯 Para usar agora, execute:")
        print("  init_genesys()")
        return True
    else:
        print("❌ Setup falhou. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    main()
else:
    # Se importado, mostrar instruções
    print("📋 Sistema de Treinamento Genesys carregado!")
    print("🚀 Execute: setup_genesys_training() para configurar")
    print("⚡ Execute: init_genesys() para inicializar rapidamente")
