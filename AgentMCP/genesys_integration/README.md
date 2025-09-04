# 🤖 Genesys Integration

**Integração da Genesys (LLaMA 70B) como Agente Master no Agent-MCP**

## 📁 Estrutura dos Arquivos

```
genesys_integration/
├── genesys_agent.py         # 🤖 Agente Genesys principal
├── genesys_server.py        # 🖥️ Servidor local FastAPI
├── genesys_bridge.py        # 🌉 Bridge MCP
├── requirements_genesys.txt # 📦 Dependências
├── models/                  # 🧠 Modelos LLaMA (links/cópias)
├── data/logs/              # 📊 Logs e interações
├── tools/                  # 🔧 Ferramentas copiadas da Genesys
└── workspace/              # 💻 Área de trabalho segura
```

## 🔧 Componentes

### **genesys_agent.py**

- **Classe Principal**: `GenesysAgent`
- **Funcionalidades**:
  - Carregamento do modelo LLaMA 70B
  - Processamento de tarefas com contexto
  - Integração com ferramentas ReAct
  - Processamento multimodal (texto + imagem)
  - Status e monitoramento

### **genesys_server.py**

- **Framework**: FastAPI + Uvicorn
- **Endpoints**:
  - `/`: Status básico
  - `/health`: Verificação de saúde
  - `/status`: Status detalhado
  - `/chat`: Chat principal
  - `/multimodal`: Processamento imagem+texto
  - `/v1/chat/completions`: Compatibilidade OpenAI/Continue
  - `/reload-model`: Recarregamento do modelo

### **genesys_bridge.py**

- **Framework**: FastMCP (MCP Server)
- **Ferramentas MCP**:
  - `genesys_chat`: Chat direto
  - `genesys_multimodal`: Processamento multimodal
  - `genesys_status`: Status do sistema
  - `create_genesys_agent`: Criar agentes especializados
  - `assign_task_to_genesys_agent`: Atribuir tarefas
  - `list_genesys_agents`: Listar agentes
  - `terminate_genesys_agent`: Encerrar agentes

## 🚀 Como Executar

### **Método 1: Sistema Integrado (Recomendado)**

```bash
# Do diretório raiz do Agent-MCP
python start_integrated.py
```

### **Método 2: Componentes Individuais**

**Servidor Genesys:**

```bash
python -m genesys_integration.genesys_server
# Acesso: http://127.0.0.1:8002
```

**Bridge MCP:**

```bash
python -m genesys_integration.genesys_bridge
# Executa como servidor MCP stdio
```

**Teste do Agente:**

```bash
python genesys_integration/genesys_agent.py
# Teste básico das funcionalidades
```

## 📋 Configuração

### **Variáveis de Ambiente (.env)**

```bash
# Modelo
MODEL_GGUF_FILENAME=llama-3-70b-instruct.Q4_K_M.gguf

# GPU
USE_GPU=true
N_GPU_LAYERS=-1

# Rede
GENESYS_LOCAL_HOST=127.0.0.1
GENESYS_LOCAL_PORT=8002

# Performance
MAX_CONTEXT_LENGTH=4096
BATCH_SIZE=512
TEMPERATURE=0.7
```

### **Dependências**

```bash
pip install -r requirements_genesys.txt
```

## 🛠️ Desenvolvimento

### **Adicionar Nova Ferramenta**

1. Implemente na Genesys original
2. Copie para `tools/`
3. Integre em `genesys_agent.py` no método `_setup_tools()`
4. Adicione endpoint em `genesys_server.py` se necessário
5. Exponha via MCP em `genesys_bridge.py`

### **Exemplo de Nova Ferramenta MCP**

```python
# Em genesys_bridge.py
@mcp.tool()
async def nova_ferramenta(param: str) -> str:
    """
    Nova funcionalidade da Genesys
    """
    data = {"prompt": f"Execute nova ferramenta: {param}"}
    result = await bridge.call_genesys("/chat", data)
    return result.get("response", "Erro")
```

### **Debug e Logs**

```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Teste individual de componentes
from genesys_integration.genesys_agent import genesys_agent
await genesys_agent.load_model()
response = await genesys_agent.process_task("Teste")
```

## 📊 APIs Disponíveis

### **REST API (FastAPI)**

```bash
# Status
GET http://127.0.0.1:8002/status

# Chat
POST http://127.0.0.1:8002/chat
{
  "prompt": "Sua pergunta",
  "context": {"key": "value"},
  "use_tools": true
}

# Multimodal
POST http://127.0.0.1:8002/multimodal
{
  "prompt": "Analise esta imagem",
  "image_data": "base64_encoded_image"
}
```

### **MCP Tools (via Agent-MCP)**

```javascript
// No dashboard Agent-MCP
genesys_chat({
  prompt: "Analise este código Python",
  context: "{'language': 'python'}",
  use_tools: true,
});
```

## 🔧 Manutenção

### **Atualizar Modelo**

1. Baixe novo modelo GGUF
2. Coloque em `models/`
3. Atualize `MODEL_GGUF_FILENAME` no `.env`
4. Reinicie: `/reload-model` ou restart completo

### **Monitorar Performance**

```bash
# Status da GPU
nvidia-smi

# Logs do servidor
tail -f data/logs/genesys.log

# Monitoramento do processo
top -p $(pgrep -f genesys_server)
```

### **Backup e Restore**

```bash
# Backup dos logs de interação (para fine-tuning)
tar -czf backup_$(date +%Y%m%d).tar.gz data/logs/

# Backup da configuração
cp .env config_backup.env
```

## 🚨 Troubleshooting

### **Modelo não carrega**

```bash
# Verificar arquivo
ls -la models/*.gguf

# Verificar memória
free -h

# Logs detalhados
python genesys_integration/genesys_agent.py
```

### **GPU não detectada**

```bash
# Verificar CUDA
nvidia-smi
nvcc --version

# Verificar PyTorch
python -c "import torch; print(torch.cuda.is_available())"

# Reinstalar llama-cpp-python com CUDA
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

### **Servidor não responde**

```bash
# Verificar porta
netstat -tlnp | grep 8002

# Teste direto
curl http://127.0.0.1:8002/health

# Logs de erro
python -m genesys_integration.genesys_server --debug
```

## 📈 Performance

### **Otimizações Implementadas**

- **GPU Layers**: `-1` (todas as camadas na GPU)
- **Batch Size**: `512` (otimizado para performance)
- **Context Length**: `4096` (equilibrio memória/capacidade)
- **Async Processing**: FastAPI + asyncio
- **Model Caching**: Modelo permanece carregado

### **Benchmarks Esperados**

- **CPU Only**: 1-5 tokens/segundo ❌
- **GPU (RTX 3060)**: 15-30 tokens/segundo ✅
- **GPU (RTX 4090)**: 50-150 tokens/segundo 🚀
- **Memory Usage**: 8-12GB VRAM para 70B Q4

## 🔮 Roadmap

### **Implementado ✅**

- [x] Integração básica com Agent-MCP
- [x] Servidor FastAPI com hot-reload
- [x] Bridge MCP com ferramentas completas
- [x] Processamento multimodal
- [x] Sistema de logging para fine-tuning

### **Em Desenvolvimento 🚧**

- [ ] Cache inteligente de respostas
- [ ] Load balancing para múltiplas GPUs
- [ ] Integração com Hugging Face Hub
- [ ] Auto-scaling baseado na demanda

### **Planejado 📋**

- [ ] Suporte para modelos quantizados GPTQ
- [ ] Integração com TensorRT para inference
- [ ] Distributed inference (múltiplas máquinas)
- [ ] Fine-tuning automático baseado em uso

---

**🎯 Esta integração transforma sua Genesys em um agente master ultra-eficiente dentro do ecossistema Agent-MCP!**
