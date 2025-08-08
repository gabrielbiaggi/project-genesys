#!/usr/bin/env python3
"""
scripts/cloudflare_tunnel_helper.py

Script auxiliar para gerenciar e testar o túnel Cloudflare do servidor Genesys.
Facilita a descoberta da URL do túnel e o teste de conectividade.

Uso:
    python scripts/cloudflare_tunnel_helper.py discover
    python scripts/cloudflare_tunnel_helper.py test
    python scripts/cloudflare_tunnel_helper.py monitor
"""

import argparse
import requests
import time
import json
import re
import subprocess
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from urllib.parse import urlparse

class CloudflareTunnelHelper:
    """Helper para gerenciar túneis Cloudflare do Genesys."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        print("🌐 Cloudflare Tunnel Helper - Projeto Genesys")
        print("=" * 60)

    def discover_tunnel_url(self, auto_save: bool = True) -> Optional[str]:
        """
        Tenta descobrir a URL do túnel Cloudflare em execução.
        
        Args:
            auto_save: Se True, salva a URL descoberta no arquivo .env
            
        Returns:
            URL do túnel se encontrada, None caso contrário
        """
        print("🔍 Descobrindo URL do túnel Cloudflare...")
        
        # Métodos de descoberta (em ordem de preferência)
        discovery_methods = [
            self._discover_from_env_file,
            self._discover_from_cloudflared_logs,
            self._discover_from_process_list,
            self._discover_from_cloudflare_api,
        ]
        
        for method in discovery_methods:
            try:
                url = method()
                if url:
                    print(f"✅ URL encontrada: {url}")
                    
                    if auto_save:
                        self._save_url_to_env(url)
                    
                    return url
                    
            except Exception as e:
                print(f"⚠️  Método falhou: {e}")
                continue
        
        print("❌ Não foi possível descobrir a URL do túnel")
        print("💡 Verifique se o túnel Cloudflare está rodando")
        return None

    def _discover_from_env_file(self) -> Optional[str]:
        """Tenta descobrir a URL do arquivo .env."""
        env_path = self.project_root / ".env"
        
        if not env_path.exists():
            return None
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Procura por URLs do Cloudflare
            patterns = [
                r'SERVER_URL\s*=\s*([^\s\n]+)',
                r'CLOUDFLARE_TUNNEL_URL\s*=\s*([^\s\n]+)',
                r'TUNNEL_URL\s*=\s*([^\s\n]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    url = match.group(1).strip('"\'')
                    if 'trycloudflare.com' in url or 'cloudflare' in url:
                        print(f"📄 URL encontrada no .env: {url}")
                        return url
            
        except Exception as e:
            print(f"⚠️  Erro ao ler .env: {e}")
        
        return None

    def _discover_from_cloudflared_logs(self) -> Optional[str]:
        """Tenta descobrir a URL dos logs do cloudflared."""
        # Possíveis locais de logs
        log_paths = [
            "C:\\ProgramData\\GenesysService\\cloudflared-stdout.log",
            "C:\\ProgramData\\GenesisService\\cloudflared-stdout.log", 
            Path.home() / ".cloudflared" / "cloudflared.log",
            "/var/log/cloudflared.log",
            "/tmp/cloudflared.log",
        ]
        
        for log_path in log_paths:
            try:
                log_path = Path(log_path)
                if not log_path.exists():
                    continue
                
                print(f"📋 Verificando log: {log_path}")
                
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Lê as últimas linhas (mais recentes)
                    lines = f.readlines()[-50:]
                
                for line in reversed(lines):
                    # Procura por URLs do túnel
                    if 'trycloudflare.com' in line:
                        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                        if match:
                            url = match.group(0)
                            print(f"📋 URL encontrada nos logs: {url}")
                            return url
                
            except Exception as e:
                print(f"⚠️  Erro ao ler log {log_path}: {e}")
                continue
        
        return None

    def _discover_from_process_list(self) -> Optional[str]:
        """Tenta descobrir a URL da lista de processos em execução."""
        try:
            if sys.platform == "win32":
                # Windows: usa wmic ou tasklist
                cmd = ["wmic", "process", "where", "name='cloudflared.exe'", "get", "commandline", "/value"]
            else:
                # Linux/Mac: usa ps
                cmd = ["ps", "aux"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Procura por URLs nas linhas de comando
                lines = output.split('\n')
                for line in lines:
                    if 'cloudflared' in line and 'tunnel' in line:
                        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                        if match:
                            url = match.group(0)
                            print(f"🔧 URL encontrada nos processos: {url}")
                            return url
            
        except Exception as e:
            print(f"⚠️  Erro ao verificar processos: {e}")
        
        return None

    def _discover_from_cloudflare_api(self) -> Optional[str]:
        """Tenta descobrir via API do Cloudflare (se token disponível)."""
        # Esta implementação requer token de API e é mais complexa
        # Por enquanto, retorna None - pode ser implementada futuramente
        return None

    def _save_url_to_env(self, url: str) -> bool:
        """Salva a URL descoberta no arquivo .env."""
        env_path = self.project_root / ".env"
        
        try:
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Atualiza ou adiciona a linha SERVER_URL
                if 'SERVER_URL=' in content:
                    content = re.sub(r'SERVER_URL\s*=\s*[^\n]*', f'SERVER_URL={url}', content)
                else:
                    content += f'\n# URL descoberta automaticamente\nSERVER_URL={url}\n'
            else:
                content = f'# URL do túnel Cloudflare\nSERVER_URL={url}\n'
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 URL salva no .env: {url}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar URL no .env: {e}")
            return False

    def test_tunnel_connectivity(self, url: Optional[str] = None) -> bool:
        """Testa a conectividade com o túnel."""
        if not url:
            url = self.discover_tunnel_url(auto_save=False)
        
        if not url:
            print("❌ Não foi possível encontrar URL para testar")
            return False
        
        print(f"🔗 Testando conectividade com: {url}")
        
        try:
            # Teste básico de conectividade
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print("✅ Túnel funcionando corretamente!")
                
                # Tenta detectar se é o servidor Genesys
                try:
                    data = response.json()
                    message = data.get('message', '')
                    if 'Genesys' in message:
                        print("🤖 Servidor Genesys detectado!")
                    else:
                        print("⚠️  Resposta inesperada do servidor")
                except:
                    print("⚠️  Servidor respondeu, mas não parece ser o Genesys")
                
                return True
                
            else:
                print(f"⚠️  Túnel responde com status {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Erro de conectividade: {e}")
            return False

    def monitor_tunnel(self, url: Optional[str] = None, interval: int = 30) -> None:
        """Monitora o túnel continuamente."""
        if not url:
            url = self.discover_tunnel_url(auto_save=False)
        
        if not url:
            print("❌ Não foi possível encontrar URL para monitorar")
            return
        
        print(f"📊 Monitorando túnel: {url}")
        print(f"⏱️  Intervalo: {interval} segundos")
        print("🛑 Pressione Ctrl+C para parar")
        print("=" * 60)
        
        try:
            while True:
                start_time = time.time()
                
                try:
                    response = requests.get(url, timeout=10)
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000
                    
                    status = "🟢" if response.status_code == 200 else "🟡"
                    timestamp = time.strftime("%H:%M:%S")
                    
                    print(f"{timestamp} | {status} Status: {response.status_code} | Latência: {latency:.2f}ms")
                    
                except requests.RequestException as e:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"{timestamp} | 🔴 ERRO: {e}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n📊 Monitoramento interrompido pelo usuário")

    def list_available_commands(self) -> None:
        """Lista todos os comandos disponíveis."""
        print("📋 Comandos disponíveis:")
        print("=" * 60)
        
        commands = [
            ("discover", "Descobre automaticamente a URL do túnel"),
            ("test", "Testa a conectividade com o túnel"),
            ("monitor", "Monitora o túnel continuamente"),
            ("help", "Mostra esta lista de comandos"),
        ]
        
        for cmd, desc in commands:
            print(f"  {cmd:12} | {desc}")
        
        print("\n💡 Exemplos de uso:")
        print("  python scripts/cloudflare_tunnel_helper.py discover")
        print("  python scripts/cloudflare_tunnel_helper.py test")
        print("  python scripts/cloudflare_tunnel_helper.py monitor")

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Helper para gerenciar túneis Cloudflare do Genesys"
    )
    
    parser.add_argument(
        "command",
        nargs='?',
        choices=["discover", "test", "monitor", "help"],
        default="help",
        help="Comando a executar"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="URL específica do túnel para testar/monitorar"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Intervalo de monitoramento em segundos (padrão: 30)"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Não salva a URL descoberta no arquivo .env"
    )
    
    args = parser.parse_args()
    
    helper = CloudflareTunnelHelper()
    
    try:
        if args.command == "discover":
            url = helper.discover_tunnel_url(auto_save=not args.no_save)
            if url:
                print(f"\n🎉 URL descoberta: {url}")
            else:
                sys.exit(1)
                
        elif args.command == "test":
            success = helper.test_tunnel_connectivity(args.url)
            sys.exit(0 if success else 1)
            
        elif args.command == "monitor":
            helper.monitor_tunnel(args.url, args.interval)
            
        elif args.command == "help":
            helper.list_available_commands()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
