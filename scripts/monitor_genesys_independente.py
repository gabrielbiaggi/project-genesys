#!/usr/bin/env python3
# scripts/monitor_genesys_independente.py
# Monitor independente do terminal para Genesys Service

import sys
import os
import time
import json
import requests
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import subprocess
import signal
import psutil

# Configurações
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SERVICE_NAME = "GenesysAI"
DEFAULT_PORT = 8002
DEFAULT_HOST = "localhost"
CLOUDFLARE_URL = "https://genesys.webcreations.com.br"

class GenesysServiceMonitor:
    """Monitor independente para o serviço Genesys"""
    
    def __init__(self, local_url: str = None, remote_url: str = None):
        self.local_url = local_url or f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"
        self.remote_url = remote_url or CLOUDFLARE_URL
        self.monitoring = True
        self.stats = {
            "start_time": datetime.now(),
            "requests_count": 0,
            "errors_count": 0,
            "last_response_time": 0,
            "service_status": "unknown",
            "api_status": "unknown"
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handler para shutdown graceful"""
        print(f"\n🛑 Recebido sinal {signum}. Finalizando monitor...")
        self.monitoring = False
        
    def check_service_status(self) -> Dict[str, Any]:
        """Verifica status do serviço Windows"""
        try:
            # Usar PowerShell para verificar serviço
            cmd = f'powershell -Command "Get-Service -Name {SERVICE_NAME} -ErrorAction SilentlyContinue | Select-Object Name,Status,StartType | ConvertTo-Json"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                service_info = json.loads(result.stdout)
                return {
                    "installed": True,
                    "status": service_info.get("Status", "Unknown"),
                    "start_type": service_info.get("StartType", "Unknown"),
                    "name": service_info.get("Name", SERVICE_NAME)
                }
            else:
                return {
                    "installed": False,
                    "status": "Not Installed",
                    "start_type": "N/A",
                    "name": SERVICE_NAME
                }
                
        except Exception as e:
            return {
                "installed": False,
                "status": "Error",
                "error": str(e),
                "name": SERVICE_NAME
            }
    
    def check_api_status(self, url: str, timeout: int = 5) -> Dict[str, Any]:
        """Verifica status da API"""
        try:
            start_time = time.time()
            response = requests.get(f"{url}/", timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # em ms
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        "status": "online",
                        "response_time_ms": round(response_time, 2),
                        "message": data.get("message", ""),
                        "agent_loaded": "não carregado" not in data.get("message", "").lower()
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "online",
                        "response_time_ms": round(response_time, 2),
                        "message": "Response not JSON",
                        "agent_loaded": False
                    }
            else:
                return {
                    "status": "error",
                    "response_time_ms": round(response_time, 2),
                    "http_code": response.status_code,
                    "agent_loaded": False
                }
                
        except requests.exceptions.ConnectIO as e:
            return {
                "status": "offline",
                "error": "Connection refused",
                "agent_loaded": False
            }
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "error": f"Timeout after {timeout}s",
                "agent_loaded": False
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_loaded": False
            }
    
    def start_service_if_needed(self) -> bool:
        """Inicia o serviço se necessário"""
        try:
            service_status = self.check_service_status()
            
            if not service_status["installed"]:
                print("❌ Serviço não está instalado!")
                print("💡 Execute: .\\scripts\\setup_genesys_service.ps1 -Action install")
                return False
            
            if service_status["status"] == "Running":
                print("✅ Serviço já está rodando")
                return True
            
            print("🚀 Iniciando serviço...")
            cmd = f'powershell -Command "Start-Service -Name {SERVICE_NAME}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Serviço iniciado com sucesso!")
                return True
            else:
                print(f"❌ Erro ao iniciar serviço: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar serviço: {e}")
            return False
    
    def display_status(self, service_info: Dict, local_api: Dict, remote_api: Dict):
        """Exibe status formatado"""
        # Limpar tela (Windows)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Header
        print("🤖 MONITOR GENESYS - SERVIÇO INDEPENDENTE")
        print("=" * 60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕒 Uptime: {datetime.now() - self.stats['start_time']}")
        print()
        
        # Status do Serviço Windows
        print("🔧 SERVIÇO WINDOWS:")
        service_color = "✅" if service_info.get("status") == "Running" else "❌"
        print(f"  {service_color} Status: {service_info.get('status', 'Unknown')}")
        print(f"  🔹 Nome: {service_info.get('name', SERVICE_NAME)}")
        if service_info.get("start_type"):
            print(f"  🔹 Tipo: {service_info['start_type']}")
        print()
        
        # Status da API Local
        print("🏠 API LOCAL:")
        local_color = "✅" if local_api.get("status") == "online" else "❌"
        print(f"  {local_color} Status: {local_api.get('status', 'unknown')}")
        print(f"  🌐 URL: {self.local_url}")
        if local_api.get("response_time_ms"):
            print(f"  ⚡ Latência: {local_api['response_time_ms']:.1f}ms")
        if local_api.get("message"):
            print(f"  💬 Mensagem: {local_api['message'][:50]}...")
        agent_status = "✅" if local_api.get("agent_loaded") else "❌"
        print(f"  🤖 Agente IA: {agent_status}")
        print()
        
        # Status da API Remota
        print("🌍 API REMOTA (CLOUDFLARE):")
        remote_color = "✅" if remote_api.get("status") == "online" else "❌"
        print(f"  {remote_color} Status: {remote_api.get('status', 'unknown')}")
        print(f"  🌐 URL: {self.remote_url}")
        if remote_api.get("response_time_ms"):
            print(f"  ⚡ Latência: {remote_api['response_time_ms']:.1f}ms")
        if remote_api.get("message"):
            print(f"  💬 Mensagem: {remote_api['message'][:50]}...")
        print()
        
        # Estatísticas
        print("📊 ESTATÍSTICAS:")
        print(f"  📈 Requisições: {self.stats['requests_count']}")
        print(f"  ❌ Erros: {self.stats['errors_count']}")
        uptime_seconds = (datetime.now() - self.stats['start_time']).total_seconds()
        if uptime_seconds > 0:
            success_rate = ((self.stats['requests_count'] - self.stats['errors_count']) / max(self.stats['requests_count'], 1)) * 100
            print(f"  ✅ Taxa de Sucesso: {success_rate:.1f}%")
        print()
        
        # Instruções
        print("🎮 CONTROLES:")
        print("  Ctrl+C - Parar monitor")
        print("  Fechar janela - Monitor continua em background")
        print("=" * 60)
    
    def save_stats(self):
        """Salva estatísticas em arquivo"""
        try:
            stats_dir = Path(PROJECT_ROOT) / "data" / "logs"
            stats_dir.mkdir(parents=True, exist_ok=True)
            stats_file = stats_dir / "monitor_stats.json"
            
            stats_data = {
                **self.stats,
                "start_time": self.stats["start_time"].isoformat(),
                "last_update": datetime.now().isoformat()
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
                
        except Exception:
            pass  # Ignorar erros de salvamento
    
    def run_monitor(self, interval: int = 10, auto_start: bool = True):
        """Executa o monitor principal"""
        print("🚀 Iniciando Monitor Genesys Independente...")
        print(f"🔄 Intervalo de verificação: {interval}s")
        print()
        
        # Tentar iniciar serviço se auto_start estiver ativado
        if auto_start:
            print("🔍 Verificando se serviço precisa ser iniciado...")
            self.start_service_if_needed()
            print()
        
        print("📺 Iniciando monitoramento visual...")
        print("💡 Pressione Ctrl+C para parar (ou feche a janela para continuar em background)")
        time.sleep(2)
        
        try:
            while self.monitoring:
                # Verificar status do serviço
                service_info = self.check_service_status()
                
                # Verificar APIs
                local_api = self.check_api_status(self.local_url)
                remote_api = self.check_api_status(self.remote_url)
                
                # Atualizar estatísticas
                self.stats["requests_count"] += 2  # local + remote
                if local_api.get("status") != "online":
                    self.stats["errors_count"] += 1
                if remote_api.get("status") != "online":
                    self.stats["errors_count"] += 1
                    
                if local_api.get("response_time_ms"):
                    self.stats["last_response_time"] = local_api["response_time_ms"]
                
                self.stats["service_status"] = service_info.get("status", "unknown")
                self.stats["api_status"] = local_api.get("status", "unknown")
                
                # Exibir status
                self.display_status(service_info, local_api, remote_api)
                
                # Salvar stats
                self.save_stats()
                
                # Aguardar próximo ciclo
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitor interrompido pelo usuário")
        finally:
            print("💾 Salvando estatísticas finais...")
            self.save_stats()
            print("✅ Monitor finalizado")

def run_background_monitor(interval: int = 30):
    """Executa monitor em background sem interface visual"""
    print("🔄 Executando monitor em background...")
    
    monitor = GenesysServiceMonitor()
    
    while True:
        try:
            service_info = monitor.check_service_status()
            local_api = monitor.check_api_status(monitor.local_url, timeout=10)
            
            # Log básico
            timestamp = datetime.now().strftime('%H:%M:%S')
            status = local_api.get("status", "unknown")
            print(f"[{timestamp}] Serviço: {service_info.get('status', 'N/A')} | API: {status}")
            
            # Tentar reiniciar se offline
            if service_info.get("status") == "Stopped":
                print("🔄 Tentando reiniciar serviço...")
                monitor.start_service_if_needed()
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitor background interrompido")
            break
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
            time.sleep(interval)

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor independente Genesys Service")
    parser.add_argument("--interval", type=int, default=10, help="Intervalo de verificação em segundos")
    parser.add_argument("--background", action="store_true", help="Executar em modo background")
    parser.add_argument("--no-auto-start", action="store_true", help="Não tentar iniciar serviço automaticamente")
    parser.add_argument("--local-url", help="URL da API local")
    parser.add_argument("--remote-url", help="URL da API remota")
    
    args = parser.parse_args()
    
    if args.background:
        run_background_monitor(args.interval)
    else:
        monitor = GenesysServiceMonitor(args.local_url, args.remote_url)
        monitor.run_monitor(args.interval, not args.no_auto_start)

if __name__ == "__main__":
    main()
