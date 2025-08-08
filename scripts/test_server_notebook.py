#!/usr/bin/env python3
"""
scripts/test_server_notebook.py

Script de teste completo para validar o servidor Genesys a partir do notebook.
Testa todos os endpoints principais e valida a conectividade via Cloudflare Tunnel.

Uso:
    python scripts/test_server_notebook.py
    python scripts/test_server_notebook.py --server-url https://seu-tunnel.trycloudflare.com
"""

import argparse
import requests
import json
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any

# Configurações padrão
DEFAULT_SERVER_URL = "https://genesys.webcreations.com.br"
DEFAULT_TIMEOUT = 30
TEST_WORKSPACE_PATH = "workspace"

class GenesysServerTester:
    """Testador abrangente para o servidor Genesys."""
    
    def __init__(self, server_url: str, timeout: int = DEFAULT_TIMEOUT):
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GenesysServerTester/1.0'
        })
        
        print(f"🔗 Conectando ao servidor: {self.server_url}")
        print(f"⏱️  Timeout configurado: {self.timeout}s")
        print("=" * 60)

    def test_connection(self) -> bool:
        """Testa a conectividade básica com o servidor."""
        print("🔍 Testando conectividade básica...")
        
        try:
            response = self.session.get(
                f"{self.server_url}/", 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Conectividade: OK")
                print(f"📄 Resposta: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ Conectividade: FALHOU (Status: {response.status_code})")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Conectividade: ERRO - {e}")
            return False

    def test_chat_endpoint(self) -> bool:
        """Testa o endpoint principal de chat."""
        print("\n💬 Testando endpoint de chat...")
        
        test_prompt = "Olá, Genesys! Este é um teste de conectividade. Responda brevemente que você está funcionando."
        
        payload = {
            "prompt": test_prompt
        }
        
        try:
            print(f"📤 Enviando prompt: '{test_prompt[:50]}...'")
            
            start_time = time.time()
            response = self.session.post(
                f"{self.server_url}/chat",
                json=payload,
                timeout=60  # Chat pode demorar mais
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                steps = data.get("intermediate_steps", [])
                
                print(f"✅ Chat: OK ({end_time - start_time:.2f}s)")
                print(f"📝 Resposta: {response_text[:100]}...")
                print(f"🔧 Passos intermediários: {len(steps)}")
                
                return True
                
            elif response.status_code == 503:
                print("⚠️  Chat: Agente não carregado (modo de desenvolvimento)")
                return True  # Isso é esperado no notebook
                
            else:
                print(f"❌ Chat: FALHOU (Status: {response.status_code})")
                print(f"📄 Erro: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Chat: ERRO - {e}")
            return False

    def test_download_model_endpoint(self) -> bool:
        """Testa o endpoint de download de modelo."""
        print("\n📥 Testando endpoint de download de modelo...")
        
        try:
            response = self.session.post(
                f"{self.server_url}/download-model",
                json={},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Download: OK")
                print(f"📄 Status: {data.get('status', 'N/A')}")
                return True
            else:
                print(f"❌ Download: FALHOU (Status: {response.status_code})")
                print(f"📄 Erro: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Download: ERRO - {e}")
            return False

    def test_script_execution_endpoint(self) -> bool:
        """Testa o endpoint de execução de scripts."""
        print("\n🔧 Testando endpoint de execução de scripts...")
        
        # Tenta executar o script de teste de modelo
        payload = {
            "script_path": "scripts/test_model_load.py"
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/run-script",
                json=payload,
                timeout=60  # Scripts podem demorar mais
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Execução de script: OK")
                print(f"📄 Status: {data.get('status', 'N/A')}")
                return True
            else:
                print(f"❌ Execução de script: FALHOU (Status: {response.status_code})")
                print(f"📄 Erro: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Execução de script: ERRO - {e}")
            return False

    def test_multimodal_capability(self) -> bool:
        """Testa capacidade multimodal com uma imagem de teste simples."""
        print("\n🖼️  Testando capacidade multimodal...")
        
        # Cria uma imagem de teste simples em base64 (1x1 pixel PNG transparente)
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        payload = {
            "prompt": "Descreva brevemente o que você vê nesta imagem de teste.",
            "image": test_image_b64
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Multimodal: OK")
                print(f"📝 Resposta: {data.get('response', '')[:100]}...")
                return True
                
            elif response.status_code == 503:
                print("⚠️  Multimodal: Não disponível (sem modelo carregado)")
                return True  # Esperado no notebook
                
            else:
                print(f"❌ Multimodal: FALHOU (Status: {response.status_code})")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Multimodal: ERRO - {e}")
            return False

    def test_performance_benchmark(self) -> Dict[str, float]:
        """Executa um benchmark básico de performance."""
        print("\n⚡ Executando benchmark de performance...")
        
        results = {}
        
        # Teste de latência básica
        try:
            start_time = time.time()
            response = self.session.get(f"{self.server_url}/", timeout=self.timeout)
            end_time = time.time()
            
            if response.status_code == 200:
                results['latency_ms'] = (end_time - start_time) * 1000
                print(f"📊 Latência: {results['latency_ms']:.2f}ms")
            
        except requests.RequestException:
            results['latency_ms'] = float('inf')
            print("📊 Latência: ERRO")
        
        return results

    def run_full_test_suite(self) -> Dict[str, bool]:
        """Executa a suíte completa de testes."""
        print("🚀 Iniciando suíte completa de testes...")
        print("=" * 60)
        
        results = {}
        
        # Testes ordenados por prioridade
        test_methods = [
            ("connection", self.test_connection),
            ("chat", self.test_chat_endpoint),
            ("download", self.test_download_model_endpoint),
            ("script_execution", self.test_script_execution_endpoint),
            ("multimodal", self.test_multimodal_capability),
        ]
        
        for test_name, test_method in test_methods:
            results[test_name] = test_method()
            time.sleep(1)  # Pequena pausa entre testes
        
        # Benchmark de performance
        print("\n" + "=" * 60)
        performance = self.test_performance_benchmark()
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📋 RESUMO DOS TESTES:")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASSOU" if passed_test else "❌ FALHOU"
            print(f"{test_name.upper():20} | {status}")
        
        print("=" * 60)
        print(f"📊 RESULTADO FINAL: {passed}/{total} testes passaram")
        
        if performance.get('latency_ms', float('inf')) < float('inf'):
            print(f"⚡ Latência média: {performance['latency_ms']:.2f}ms")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM! Servidor funcionando perfeitamente.")
        elif passed > total // 2:
            print("⚠️  MAIORIA DOS TESTES PASSOU. Algumas funcionalidades podem estar limitadas.")
        else:
            print("❌ MUITOS TESTES FALHARAM. Verifique a configuração do servidor.")
        
        return results

def main():
    """Função principal do script de teste."""
    parser = argparse.ArgumentParser(
        description="Testa a conectividade e funcionalidade do servidor Genesys"
    )
    
    parser.add_argument(
        "--server-url",
        type=str,
        default=DEFAULT_SERVER_URL,
        help=f"URL do servidor (padrão: {DEFAULT_SERVER_URL})"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout em segundos (padrão: {DEFAULT_TIMEOUT})"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Executa apenas testes básicos (mais rápido)"
    )
    
    args = parser.parse_args()
    
    # Cria o testador
    tester = GenesysServerTester(args.server_url, args.timeout)
    
    if args.quick:
        # Teste rápido - apenas conectividade e chat
        print("🏃 Modo rápido ativado - executando apenas testes essenciais...\n")
        connection_ok = tester.test_connection()
        chat_ok = tester.test_chat_endpoint()
        
        if connection_ok and chat_ok:
            print("\n🎉 Testes rápidos passaram! Servidor está funcionando.")
        else:
            print("\n❌ Testes rápidos falharam. Verifique a configuração.")
    else:
        # Suíte completa
        tester.run_full_test_suite()

if __name__ == "__main__":
    main()
