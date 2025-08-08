#!/usr/bin/env python3
"""
test_genesys_quick.py

Teste rápido e simples para verificar se o servidor Genesys está funcionando.
Use este script para testes instantâneos.

Uso:
    python test_genesys_quick.py
"""

import requests
import time

def test_genesys():
    """Teste rápido do servidor Genesys."""
    print("🤖 Teste Rápido do Genesys")
    print("=" * 30)
    
    # URL do seu túnel Cloudflare
    url = "https://genesys.webcreations.com.br"
    
    try:
        print(f"🔗 Testando: {url}")
        
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', 'N/A')
            
            print(f"✅ Status: OK")
            print(f"⚡ Latência: {latency:.2f}ms")
            print(f"📄 Resposta: {message}")
            
            # Teste básico de chat
            print("\n💬 Testando chat...")
            chat_data = {"prompt": "Olá! Você está funcionando?"}
            
            try:
                chat_response = requests.post(f"{url}/chat", json=chat_data, timeout=30)
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    print(f"✅ Chat: OK")
                    print(f"🤖 Resposta: {chat_result.get('response', 'N/A')[:100]}...")
                elif chat_response.status_code == 503:
                    print("⚠️  Chat: Agente não carregado (modo desenvolvimento)")
                else:
                    print(f"❌ Chat: Erro {chat_response.status_code}")
            except:
                print("❌ Chat: Erro de conexão")
            
            print("\n🎉 Genesys está funcionando!")
            return True
            
        else:
            print(f"❌ Status: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Erro: {e}")
        print("💡 Verifique se o servidor está rodando")
        return False

if __name__ == "__main__":
    test_genesys()
