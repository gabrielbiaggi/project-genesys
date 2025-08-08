# 🚀 Genesys Server - Guia de Inicialização

Este guia é para **inicializar o servidor Genesys no seu servidor principal** com o modelo de IA de 70B.

## 🎯 Objetivo

Fornecer scripts automatizados para iniciar rapidamente o servidor Genesys com todos os componentes necessários, deixando a IA disponível via API local e túnel Cloudflare.

## 📋 Pré-requisitos

- Python 3.8+ com ambiente virtual configurado
- Modelo de IA baixado (GGUF)
- WSL2 + CUDA (se usando GPU)
- Túnel Cloudflare ativo: `https://genesys.webcreations.com.br`

## 🚀 Inicialização Rápida

### Opção 1: Script Batch (Simples)
```cmd
start_genesys.bat
```

### Opção 2: Script PowerShell (Avançado)
```powershell
.\start_genesys.ps1
```

### Opção 3: Script Python (Completo)
```bash
python scripts/start_genesys_server.py
```

## 📋 Comandos Disponíveis

### Script PowerShell Completo
```powershell
# Inicialização padrão
.\start_genesys.ps1

# Porta personalizada
.\start_genesys.ps1 -Port 8003

# Apenas verificar modelos
.\start_genesys.ps1 -CheckOnly

# Não baixar modelo automaticamente
.\start_genesys.ps1 -NoDownload

# Host específico
.\start_genesys.ps1 -Host "127.0.0.1" -Port 8002
```

### Script Python Detalhado
```bash
# Inicialização completa
python scripts/start_genesys_server.py

# Porta personalizada
python scripts/start_genesys_server.py --port 8003

# Apenas verificar modelos
python scripts/start_genesys_server.py --model-check-only

# Host específico
python scripts/start_genesys_server.py --host 0.0.0.0 --port 8002
```

## 🔧 O Que os Scripts Fazem

### ✅ Verificações Automáticas
1. **Ambiente Virtual**: Verifica se existe e está configurado
2. **Dependências**: Instala pacotes faltantes automaticamente
3. **Modelo de IA**: Verifica se o arquivo GGUF existe
4. **Porta Disponível**: Confirma que a porta está livre
5. **Download Automático**: Baixa o modelo se necessário

### 🚀 Inicialização do Servidor
1. **Ativação do Ambiente**: Ativa o venv automaticamente
2. **Carregamento do Modelo**: Carrega o modelo de IA na memória
3. **API FastAPI**: Inicia o servidor na porta especificada
4. **Monitoramento**: Exibe logs em tempo real
5. **Parada Limpa**: Ctrl+C para parar graciosamente

## 📊 URLs de Acesso

Após a inicialização bem-sucedida:

| Acesso | URL | Descrição |
|--------|-----|-----------|
| **Local** | `http://localhost:8002` | Acesso direto ao servidor |
| **Túnel** | `https://genesys.webcreations.com.br` | Acesso via Cloudflare |
| **Docs** | `http://localhost:8002/docs` | Documentação da API |
| **Health** | `http://localhost:8002/` | Status do servidor |

## 🧪 Testando o Servidor

### Teste Rápido Local
```bash
curl http://localhost:8002/
```

### Teste via Túnel
```bash
curl https://genesys.webcreations.com.br/
```

### Teste Completo
```bash
python scripts/test_server_notebook.py --server-url https://genesys.webcreations.com.br
```

## 🔍 Monitoramento e Logs

### Verificar Status
```powershell
# Ver processos Python rodando
Get-Process python

# Ver uso da porta
Get-NetTCPConnection -LocalPort 8002
```

### Logs do Servidor
Os logs são exibidos em tempo real no terminal. Para salvar:
```bash
python scripts/start_genesys_server.py 2>&1 | Tee-Object -FilePath "genesys_server.log"
```

## 🛠️ Solução de Problemas

### Problema: "Ambiente virtual não encontrado"
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar e instalar dependências
venv\Scripts\activate
pip install -r requirements.txt
```

### Problema: "Modelo não encontrado"
```bash
# Baixar modelo automaticamente
python scripts/download_model.py

# Ou verificar diretório de modelos
dir models\*.gguf
```

### Problema: "Porta em uso"
```powershell
# Ver o que está usando a porta
Get-NetTCPConnection -LocalPort 8002 | Select-Object OwningProcess
Get-Process -Id [PID]

# Para o processo
Stop-Process -Id [PID] -Force

# Ou usar porta diferente
.\start_genesys.ps1 -Port 8003
```

### Problema: "Erro de memória/GPU"
```bash
# Verificar uso de memória
nvidia-smi

# Verificar modelos grandes
dir models\*.gguf | ForEach-Object { "{0:N1} GB - {1}" -f ($_.Length/1GB), $_.Name }
```

## ⚙️ Configuração Avançada

### Variáveis de Ambiente (.env)
```env
# Configuração do servidor
API_HOST=0.0.0.0
API_PORT=8002

# Modelo de IA
HUGGING_FACE_REPO_ID=mindrage/Llama-3-70B-Instruct-v2-LLaVA-GGUF
MODEL_GGUF_FILENAME=Llama-3-70B-Instruct-v2-Q4_K_M.gguf

# URLs
SERVER_URL=https://genesys.webcreations.com.br
LOCAL_MODEL_ENDPOINT=http://localhost:8002/v1
```

### Configuração de Performance
Para otimizar o desempenho:

1. **CPU Only**: Use modelos menores (8B-13B)
2. **GPU Híbrida**: Use offloading para RAM
3. **GPU Completa**: Carregue modelo inteiro na VRAM

## 🔄 Ciclo de Desenvolvimento

### 1. Desenvolvimento
```bash
# Inicia com reload automático
python scripts/start_genesys_server.py
```

### 2. Teste
```bash
# Testa remotamente
python scripts/test_server_notebook.py --quick
```

### 3. Deploy
```bash
# Para o servidor
Ctrl+C

# Reinicia
.\start_genesys.ps1
```

## 🎯 Próximos Passos

Após o servidor estar funcionando:

1. **Configure AutoGen**: `python autogen_logic/main.py`
2. **Teste Multimodal**: Envie imagens via API
3. **Fine-tune**: Execute `python scripts/fine_tune.py`
4. **Monitore**: Configure alertas automáticos

---

## 📞 Comandos de Emergência

### Parar Tudo
```powershell
# Para todos os processos Python
Get-Process python | Stop-Process -Force

# Libera a porta
Get-NetTCPConnection -LocalPort 8002 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### Reset Completo
```bash
# Remove ambiente e recria
Remove-Item venv -Recurse -Force
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**🎉 Seu servidor Genesys está pronto para dominar o mundo!**
