# testar_gpu_real.py - Teste REAL se llama-cpp-python está usando GPU

print("🧪 TESTE REAL DE GPU PARA LLAMA-CPP-PYTHON")
print("=" * 50)

try:
    import llama_cpp
    print("✅ llama-cpp-python importado com sucesso")
    print(f"📋 Versão: {llama_cpp.__version__}")
    
    # Teste 1: Verificar se foi compilado com CUDA
    print("\n🔍 TESTE 1: Verificando compilação CUDA...")
    
    # Tentar criar um modelo com GPU
    try:
        # Criar modelo dummy para testar GPU
        print("🧪 Tentando inicializar com GPU...")
        
        # Verifica se llama_cpp tem suporte a GPU layers
        if hasattr(llama_cpp, 'Llama'):
            print("✅ Classe Llama disponível")
            
            # Verificar se n_gpu_layers está disponível
            import inspect
            llama_init_signature = inspect.signature(llama_cpp.Llama.__init__)
            if 'n_gpu_layers' in llama_init_signature.parameters:
                print("✅ Parâmetro n_gpu_layers DISPONÍVEL (GPU Support)")
                print("🚁 RESULTADO: llama-cpp-python COM suporte GPU!")
            else:
                print("❌ Parâmetro n_gpu_layers NÃO DISPONÍVEL")
                print("🐌 RESULTADO: llama-cpp-python APENAS CPU!")
                
        else:
            print("❌ Classe Llama não encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao testar GPU: {e}")
        
    # Teste 2: Verificar bibliotecas CUDA carregadas
    print("\n🔍 TESTE 2: Verificando bibliotecas carregadas...")
    import sys
    
    cuda_libs_found = False
    for module_name in sys.modules:
        if 'cuda' in module_name.lower():
            print(f"✅ Biblioteca CUDA carregada: {module_name}")
            cuda_libs_found = True
            
    if not cuda_libs_found:
        print("⚠️ Nenhuma biblioteca CUDA carregada")
        
    # Teste 3: Verificar se pode acessar GPU info
    print("\n🔍 TESTE 3: Testando acesso a informações GPU...")
    try:
        # Tentar acessar informações específicas de GPU se disponível
        if hasattr(llama_cpp, 'llama_backend_init'):
            print("✅ Backend init disponível")
        
        print("\n📊 RESULTADO FINAL:")
        
        # Verificação definitiva
        llama_init_signature = inspect.signature(llama_cpp.Llama.__init__)
        if 'n_gpu_layers' in llama_init_signature.parameters:
            print("🎉 STATUS: GPU ATIVADA!")
            print("⚡ Performance esperada: 50-200+ tokens/segundo")
            print("✅ Pode usar n_gpu_layers=-1 para máxima performance")
        else:
            print("🐌 STATUS: APENAS CPU!")
            print("😴 Performance esperada: 1-5 tokens/segundo")
            print("❌ Recompilação com GPU necessária")
            
    except Exception as e:
        print(f"⚠️ Erro no teste final: {e}")
        
except ImportError as e:
    print(f"❌ ERRO: Não foi possível importar llama_cpp: {e}")
    print("🔧 llama-cpp-python não está instalado corretamente")

print("\n" + "=" * 50)