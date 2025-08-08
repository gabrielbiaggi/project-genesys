#!/usr/bin/env python3
# testar_genesys_completo.py
# Teste completo do sistema Genesys (local e remoto)

import requests
import json
import sys
import argparse
from typing import Optional

def test_basic_endpoint(base_url: str) -> bool:
    """Testa endpoint básico de status"""
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_chat_endpoint(base_url: str) -> bool:
    """Testa endpoint de chat original"""
    print(f"\n🧪 Testando Chat Original: {base_url}/chat")
    try:
        payload = {"prompt": "Olá! Teste rápido."}
        response = requests.post(f"{base_url}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta: {data.get('response', 'N/A')[:100]}...")
            return True
        elif response.status_code == 503:
            print("⚠️ Servidor em modo desenvolvimento (sem modelo carregado)")
            return False
        else:
            print(f"❌ Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_continue_endpoint(base_url: str) -> bool:
    """Testa endpoint Continue/OpenAI"""
    print(f"\n🧪 Testando Continue API: {base_url}/v1/chat/completions")
    
    payload = {
        "model": "genesys-local",
        "messages": [{"role": "user", "content": "Teste Continue API"}]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-dummy-key-not-needed"
    }
    
    try:
        response = requests.post(f"{base_url}/v1/chat/completions", 
                               json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                print(f"✅ Continue API funcionando!")
                print(f"🤖 Resposta: {content[:100]}...")
                return True
            else:
                print("❌ Formato de resposta inválido")
                return False
        elif response.status_code == 404:
            print("⚠️ Endpoint Continue não encontrado (API não atualizada)")
            return False
        elif response.status_code == 503:
            print("⚠️ Servidor em modo desenvolvimento")
            return False
        else:
            print(f"❌ Erro {response.status_code}")
            try:
                print(f"📄 Detalhes: {response.json()}")
            except:
                print(f"📄 Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_gpu_status() -> bool:
    """Testa se GPU está disponível"""
    print(f"\n🎮 Testando Status da GPU...")
    try:
        # Tentar importar e testar llama-cpp-python
        try:
            from llama_cpp import Llama
            print("✅ llama-cpp-python importado com sucesso")
            
            # Verificar se GPU está disponível
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ nvidia-smi funcionando - GPU disponível")
                return True
            else:
                print("⚠️ nvidia-smi não funcionou")
                return False
                
        except ImportError:
            print("⚠️ llama-cpp-python não instalado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar GPU: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Teste completo do sistema Genesys')
    parser.add_argument('--local', action='store_true', help='Testar servidor local')
    parser.add_argument('--remoto', action='store_true', help='Testar servidor remoto')
    parser.add_argument('--gpu', action='store_true', help='Testar GPU')
    parser.add_argument('--all', action='store_true', help='Testar tudo')
    
    args = parser.parse_args()
    
    # Se nenhum argumento, testar remoto por padrão
    if not any([args.local, args.remoto, args.gpu, args.all]):
        args.remoto = True
    
    print("🤖 TESTE COMPLETO DO SISTEMA GENESYS")
    print("=" * 60)
    
    results = {}
    
    # Teste GPU
    if args.gpu or args.all:
        results['gpu'] = test_gpu_status()
    
    # Teste Local
    if args.local or args.all:
        print(f"\n🏠 TESTANDO SERVIDOR LOCAL")
        print("-" * 40)
        local_url = "http://localhost:8002"
        
        print(f"🌐 Conectividade: {local_url}")
        local_basic = test_basic_endpoint(local_url)
        local_chat = test_chat_endpoint(local_url) if local_basic else False
        local_continue = test_continue_endpoint(local_url) if local_basic else False
        
        results['local'] = {
            'basic': local_basic,
            'chat': local_chat,
            'continue': local_continue
        }
    
    # Teste Remoto
    if args.remoto or args.all:
        print(f"\n🌍 TESTANDO SERVIDOR REMOTO (CLOUDFLARE)")
        print("-" * 40)
        remote_url = "https://genesys.webcreations.com.br"
        
        print(f"🌐 Conectividade: {remote_url}")
        remote_basic = test_basic_endpoint(remote_url)
        remote_chat = test_chat_endpoint(remote_url) if remote_basic else False
        remote_continue = test_continue_endpoint(remote_url) if remote_basic else False
        
        results['remoto'] = {
            'basic': remote_basic,
            'chat': remote_chat,
            'continue': remote_continue
        }
    
    # Resumo
    print(f"\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    if 'gpu' in results:
        status = "✅ OK" if results['gpu'] else "❌ ERRO"
        print(f"🎮 GPU Support: {status}")
    
    if 'local' in results:
        local_total = sum(results['local'].values())
        print(f"🏠 Local ({local_total}/3):")
        print(f"  - Conectividade: {'✅' if results['local']['basic'] else '❌'}")
        print(f"  - Chat Original: {'✅' if results['local']['chat'] else '❌'}")
        print(f"  - Continue API:  {'✅' if results['local']['continue'] else '❌'}")
    
    if 'remoto' in results:
        remote_total = sum(results['remoto'].values())
        print(f"🌍 Remoto ({remote_total}/3):")
        print(f"  - Conectividade: {'✅' if results['remoto']['basic'] else '❌'}")
        print(f"  - Chat Original: {'✅' if results['remoto']['chat'] else '❌'}")
        print(f"  - Continue API:  {'✅' if results['remoto']['continue'] else '❌'}")
    
    print("\n" + "=" * 60)
    
    # Recomendações
    if 'remoto' in results:
        if results['remoto']['basic'] and not results['remoto']['continue']:
            print("💡 RECOMENDAÇÃO:")
            print("   O servidor remoto precisa ser atualizado com a nova API Continue")
            print("   Enquanto isso, use a extensão Genesys personalizada")
        elif results['remoto']['continue']:
            print("🎉 PRONTO PARA USAR!")
            print("   Configure o Continue: .\\configurar_continue.ps1 -Mode remoto")
    
    if 'local' in results and results['local']['basic']:
        print("💻 LOCAL DISPONÍVEL:")
        print("   Configure o Continue: .\\configurar_continue.ps1 -Mode local")
    
    # Exit code baseado nos resultados
    success = False
    if 'remoto' in results and any(results['remoto'].values()):
        success = True
    if 'local' in results and any(results['local'].values()):
        success = True
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
