#!/usr/bin/env python3
# start_integrated.py
"""
Script de inicialização integrada para Genesys + Agent-MCP
Inicia todos os componentes de forma coordenada
"""
import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from typing import Optional

# Adicionar o diretório atual ao Python path
sys.path.insert(0, str(Path(__file__).parent))

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str, color: str = Colors.WHITE):
    """Imprime mensagem com cor"""
    print(f"{color}{message}{Colors.END}")

def print_header():
    """Imprime header do sistema"""
    print_status("\n" + "="*70, Colors.CYAN)
    print_status("🚀 SISTEMA INTEGRADO GENESYS + AGENT-MCP", Colors.CYAN + Colors.BOLD)
    print_status("="*70, Colors.CYAN)
    print_status("🤖 Genesys: LLaMA 70B Local + Ferramentas", Colors.WHITE)
    print_status("🧠 Agent-MCP: Orquestração Multi-Agente", Colors.WHITE)
    print_status("🌉 Bridge: Integração via MCP Protocol", Colors.WHITE)
    print_status("="*70 + "\n", Colors.CYAN)

def check_dependencies() -> bool:
    """Verifica se as dependências estão instaladas"""
    print_status("🔍 Verificando dependências...", Colors.YELLOW)
    
    required_packages = [
        "fastapi", "uvicorn", "torch", "transformers", 
        "mcp", "requests", "python-dotenv"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print_status(f"  ✅ {package}", Colors.GREEN)
        except ImportError:
            missing.append(package)
            print_status(f"  ❌ {package}", Colors.RED)
    
    if missing:
        print_status("\n❌ Dependências faltando!", Colors.RED)
        print_status("Execute:", Colors.YELLOW)
        print_status(f"  pip install -r genesys_integration/requirements_genesys.txt", Colors.WHITE)
        return False
    
    print_status("✅ Todas as dependências verificadas!\n", Colors.GREEN)
    return True

def check_genesys_model() -> bool:
    """Verifica se o modelo Genesys está disponível"""
    print_status("🧠 Verificando modelo Genesys...", Colors.YELLOW)
    
    # Caminhos possíveis para o modelo
    possible_paths = [
        "C:/DEVBill/Projetos/Genesys/models/llama-3-70b-instruct.Q4_K_M.gguf",
        "C:/DEVBill/Projetos/Genesys/models/Llama-3-8B-Instruct-SP-32k-Q4_K_M.gguf",
        "./genesys_integration/models/llama-3-70b-instruct.Q4_K_M.gguf"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            size_gb = os.path.getsize(path) / (1024**3)
            print_status(f"  ✅ Modelo encontrado: {path}", Colors.GREEN)
            print_status(f"  📊 Tamanho: {size_gb:.1f} GB", Colors.WHITE)
            return True
    
    print_status("  ⚠️ Modelo não encontrado nos caminhos esperados", Colors.YELLOW)
    print_status("  💡 O sistema tentará baixar automaticamente", Colors.CYAN)
    return True  # Não bloquear a inicialização

def wait_for_service(url: str, name: str, max_attempts: int = 30) -> bool:
    """Aguarda um serviço ficar disponível"""
    print_status(f"⏳ Aguardando {name}...", Colors.YELLOW)
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_status(f"  ✅ {name} disponível!", Colors.GREEN)
                return True
        except (requests.RequestException, requests.ConnectionError, requests.Timeout):
            pass
        
        if attempt < max_attempts - 1:
            print_status(f"  ⏳ Tentativa {attempt + 1}/{max_attempts}...", Colors.YELLOW)
            time.sleep(2)
    
    print_status(f"  ❌ {name} não respondeu", Colors.RED)
    return False

def start_genesys_server() -> Optional[subprocess.Popen]:
    """Inicia o servidor Genesys em segundo plano"""
    print_status("🤖 Iniciando Servidor Genesys...", Colors.CYAN)
    
    try:
        # Comando para iniciar servidor Genesys
        cmd = [
            sys.executable, "-m", "genesys_integration.genesys_server"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(Path(__file__).parent),
            env=os.environ.copy()
        )
        
        # Aguardar servidor ficar disponível
        if wait_for_service("http://127.0.0.1:8002/health", "Servidor Genesys"):
            print_status("✅ Servidor Genesys iniciado!", Colors.GREEN)
            return process
        else:
            process.terminate()
            return None
            
    except Exception as e:
        print_status(f"❌ Erro ao iniciar Servidor Genesys: {e}", Colors.RED)
        return None

def start_agent_mcp() -> Optional[subprocess.Popen]:
    """Inicia o Agent-MCP"""
    print_status("🧠 Iniciando Agent-MCP...", Colors.CYAN)
    
    try:
        # Comando para iniciar Agent-MCP
        cmd = [
            "uv", "run", "-m", "agent_mcp.cli", 
            "--project-dir", str(Path(__file__).parent),
            "--port", "8080"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(Path(__file__).parent),
            env=os.environ.copy()
        )
        
        # Aguardar servidor ficar disponível
        if wait_for_service("http://127.0.0.1:8080", "Agent-MCP"):
            print_status("✅ Agent-MCP iniciado!", Colors.GREEN)
            return process
        else:
            process.terminate()
            return None
            
    except Exception as e:
        print_status(f"❌ Erro ao iniciar Agent-MCP: {e}", Colors.RED)
        return None

def start_dashboard() -> Optional[subprocess.Popen]:
    """Inicia o dashboard do Agent-MCP"""
    print_status("📊 Iniciando Dashboard...", Colors.CYAN)
    
    try:
        dashboard_path = Path(__file__).parent / "agent_mcp" / "dashboard"
        
        if not dashboard_path.exists():
            print_status("⚠️ Diretório do dashboard não encontrado", Colors.YELLOW)
            return None
        
        # Comando para iniciar dashboard
        cmd = ["npm", "run", "dev"]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(dashboard_path),
            env=os.environ.copy()
        )
        
        # Aguardar dashboard ficar disponível
        time.sleep(5)  # Dashboard demora um pouco mais
        if wait_for_service("http://127.0.0.1:3847", "Dashboard", max_attempts=15):
            print_status("✅ Dashboard iniciado!", Colors.GREEN)
            return process
        else:
            print_status("⚠️ Dashboard pode não estar totalmente carregado", Colors.YELLOW)
            return process  # Retornar mesmo assim
            
    except Exception as e:
        print_status(f"❌ Erro ao iniciar Dashboard: {e}", Colors.RED)
        return None

def show_access_info():
    """Mostra informações de acesso"""
    print_status("\n" + "="*70, Colors.GREEN)
    print_status("🎉 SISTEMA INTEGRADO INICIADO COM SUCESSO!", Colors.GREEN + Colors.BOLD)
    print_status("="*70, Colors.GREEN)
    
    print_status("\n📋 URLS DE ACESSO:", Colors.CYAN + Colors.BOLD)
    print_status("🤖 Genesys API:     http://127.0.0.1:8002", Colors.WHITE)
    print_status("🤖 Genesys Status:  http://127.0.0.1:8002/status", Colors.WHITE)
    print_status("🧠 Agent-MCP:       http://127.0.0.1:8080", Colors.WHITE)
    print_status("📊 Dashboard:       http://127.0.0.1:3847", Colors.WHITE)
    
    print_status("\n🚀 PRÓXIMOS PASSOS:", Colors.CYAN + Colors.BOLD)
    print_status("1. Abra o dashboard: http://127.0.0.1:3847", Colors.WHITE)
    print_status("2. Verifique status da Genesys: http://127.0.0.1:8002/status", Colors.WHITE)
    print_status("3. Use as ferramentas MCP para criar agentes especializados", Colors.WHITE)
    print_status("4. Teste a orquestração multi-agente", Colors.WHITE)
    
    print_status("\n🔧 FERRAMENTAS MCP DISPONÍVEIS:", Colors.CYAN + Colors.BOLD)
    print_status("- genesys_chat: Conversa direta com Genesys", Colors.WHITE)
    print_status("- genesys_multimodal: Processamento de imagens", Colors.WHITE)
    print_status("- create_genesys_agent: Criar agentes especializados", Colors.WHITE)
    print_status("- assign_task_to_genesys_agent: Atribuir tarefas", Colors.WHITE)
    print_status("- genesys_status: Verificar status do sistema", Colors.WHITE)
    
    print_status("\n⚠️ IMPORTANTE:", Colors.YELLOW + Colors.BOLD)
    print_status("- Mantenha esta janela aberta para o sistema funcionar", Colors.YELLOW)
    print_status("- Use Ctrl+C para encerrar todos os serviços", Colors.YELLOW)
    print_status("- Primeira execução pode demorar para carregar modelo", Colors.YELLOW)

def cleanup_processes(processes: list):
    """Limpa processos ao encerrar"""
    print_status("\n🛑 Encerrando serviços...", Colors.YELLOW)
    
    for name, process in processes:
        if process and process.poll() is None:
            print_status(f"  🛑 Encerrando {name}...", Colors.YELLOW)
            process.terminate()
            
            # Aguardar término gracioso
            try:
                process.wait(timeout=5)
                print_status(f"  ✅ {name} encerrado", Colors.GREEN)
            except subprocess.TimeoutExpired:
                print_status(f"  ⚠️ Forçando encerramento de {name}...", Colors.YELLOW)
                process.kill()

def main():
    """Função principal"""
    print_header()
    
    # Verificações iniciais
    if not check_dependencies():
        sys.exit(1)
    
    check_genesys_model()
    
    # Lista para manter track dos processos
    processes = []
    
    try:
        # 1. Iniciar Servidor Genesys
        genesys_process = start_genesys_server()
        if genesys_process:
            processes.append(("Servidor Genesys", genesys_process))
        else:
            print_status("❌ Falha crítica: Servidor Genesys não iniciou", Colors.RED)
            sys.exit(1)
        
        # 2. Iniciar Agent-MCP
        agent_mcp_process = start_agent_mcp()
        if agent_mcp_process:
            processes.append(("Agent-MCP", agent_mcp_process))
        else:
            print_status("❌ Falha crítica: Agent-MCP não iniciou", Colors.RED)
            cleanup_processes(processes)
            sys.exit(1)
        
        # 3. Iniciar Dashboard (opcional)
        dashboard_process = start_dashboard()
        if dashboard_process:
            processes.append(("Dashboard", dashboard_process))
        
        # Mostrar informações de acesso
        show_access_info()
        
        # Aguardar interrupção
        print_status(f"\n{Colors.CYAN}Pressione Ctrl+C para encerrar o sistema{Colors.END}")
        
        # Loop principal - monitorar processos
        while True:
            time.sleep(5)
            
            # Verificar se algum processo morreu
            for name, process in processes:
                if process.poll() is not None:
                    print_status(f"⚠️ {name} parou inesperadamente", Colors.YELLOW)
            
    except KeyboardInterrupt:
        print_status("\n🛑 Interrupção recebida (Ctrl+C)", Colors.YELLOW)
    except Exception as e:
        print_status(f"\n❌ Erro inesperado: {e}", Colors.RED)
    finally:
        cleanup_processes(processes)
        print_status("\n✅ Sistema encerrado", Colors.GREEN)

if __name__ == "__main__":
    main()
