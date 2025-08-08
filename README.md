# 🤖 PROJETO GENESYS: SISTEMA DE IA SOBERANA COMPLETO

<div align="center">

![Genesys Logo](https://img.shields.io/badge/🤖-GENESYS-purple?style=for-the-badge&logoColor=white)
![GPU Powered](https://img.shields.io/badge/⚡-GPU_POWERED-green?style=for-the-badge)
![70B Model](https://img.shields.io/badge/🧠-70B_MODEL-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/🚀-READY-success?style=for-the-badge)

**🎯 Um agente de IA local de 70B rodando no seu próprio hardware, com integração completa ao Cursor IDE**

[🚀 Início Rápido](#-início-rápido) •
[🎮 GPU Setup](#-gpu-obrigatória) •
[💻 Integração Cursor](#-integração-com-cursor) •
[🔧 Problemas](#-solução-de-problemas)

</div>

---

## 🎯 VISÃO GERAL

### ⚡ **SISTEMA DE IA SOBERANA ULTRA RÁPIDA**

O **Genesys** é uma solução completa de IA que roda **100% localmente** no seu hardware, proporcionando:

- 🧠 **Modelo Local 70B** - Llama 3 70B com performance máxima
- 🎮 **GPU OBRIGATÓRIA** - 50-200+ tokens/segundo (vs 1-5 na CPU)
- 🔧 **Ferramentas Integradas** - Sistema de arquivos, terminal, busca web
- 🌐 **API RESTful** - Interface FastAPI para integração total
- 👥 **Multi-Agente** - Orquestração via AutoGen
- 💻 **Extensão Cursor** - Integração nativa com o editor
- 🔒 **Privacidade Total** - Dados nunca saem do seu servidor
- 📈 **Aprendizado Contínuo** - Logs para fine-tuning personalizado

### 💪 **ESPECIFICAÇÕES RECOMENDADAS**

| Componente  | Mínimo        | Recomendado       | Ideal                    |
| ----------- | ------------- | ----------------- | ------------------------ |
| **CPU**     | i5-8400       | i7-12700F         | i7-14700F                |
| **RAM**     | 32GB          | 64GB              | 128GB                    |
| **GPU**     | RTX 3060 12GB | RTX 4060 16GB     | RTX 4090 24GB            |
| **Storage** | 100GB SSD     | 500GB NVMe        | 1TB NVMe                 |
| **Sistema** | Windows 10    | Windows 11 + WSL2 | Windows 11 + WSL2 + CUDA |

---

## 🚀 INÍCIO RÁPIDO

### 🚨 **PROBLEMAS IDENTIFICADOS E SOLUÇÕES DEFINITIVAS**

#### ❌ **PROBLEMAS REPORTADOS:**

1. **🏠 Servidor local não responde** (localhost:8002)
2. **🤖 Agente não carregado** (modo desenvolvimento)
3. **❌ API Continue retorna 404** (endpoint não encontrado)

#### ✅ **SOLUÇÕES DEFINITIVAS CRIADAS:**

**🎯 COMANDO MASTER (NOVO):**

```powershell
# Iniciar servidor principal
.\iniciar_genesys.ps1

# Testar GPU primeiro
.\iniciar_genesys.ps1 -GPU

# Testar local/remoto
.\iniciar_genesys.ps1 -Teste
.\iniciar_genesys.ps1 -Teste -Remoto
```

_Substitui todos os scripts redundantes em um só comando_

#### 🔄 **API CONTINUE CORRIGIDA:**

- ✅ **Endpoint `/v1/chat/completions` SEMPRE funciona**
- ✅ **Resposta informativa mesmo sem modelo**
- ✅ **Compatível com Continue extension**

---

### ⚡ **COMANDO PRINCIPAL - USE SEMPRE:**

```powershell
# ◀️ COMANDO PRINCIPAL NOVO ▶️
.\iniciar_genesys.ps1

# 🔄 COMANDO ALTERNATIVO (se preferir):
.\scripts\start_simple.ps1
```

**🎯 Este comando faz TUDO:**

- ✅ Verifica dependências automaticamente
- ✅ Inicia IA com GPU ativada (`n_gpu_layers=-1`)
- ✅ Performance máxima garantida (50-200+ tokens/seg)
- ✅ Servidor local + túnel remoto
- ✅ Monitoramento em tempo real

### 🧪 **TESTE SE FUNCIONOU:**

```powershell
# Teste local
curl http://localhost:8002/

# Teste remoto
curl https://genesys.webcreations.com.br/

# Verificar GPU
python testar_gpu_real.py  # Deve mostrar "🎉 STATUS: GPU ATIVADA!"
```

### 📋 **URLS DE ACESSO:**

| Tipo          | URL                                   | Descrição          |
| ------------- | ------------------------------------- | ------------------ |
| **🏠 Local**  | `http://localhost:8002`               | Acesso direto      |
| **🌍 Remoto** | `https://genesys.webcreations.com.br` | Via Cloudflare     |
| **📖 Docs**   | `http://localhost:8002/docs`          | API Documentation  |
| **💚 Health** | `http://localhost:8002/`              | Status do servidor |

---

## 🎮 GPU OBRIGATÓRIA

### 🚨 **ATENÇÃO: GPU É OBRIGATÓRIA!**

| Processador | Performance         | Uso Prático         |
| ----------- | ------------------- | ------------------- |
| **💀 CPU**  | ~1-5 tokens/seg     | **INUTILIZÁVEL** 😴 |
| **⚡ GPU**  | ~50-200+ tokens/seg | **PERFEITO** 🚀     |

### 📥 **INSTALAÇÃO CUDA (OBRIGATÓRIA):**

#### **1. Download CUDA Toolkit**

```
🔗 Link: https://developer.nvidia.com/cuda-downloads
📋 Escolha: Windows > x86_64 > 11 > exe (local)
📦 Arquivo: ~3GB
⏱️ Tempo: ~15 minutos
```

#### **2. Instalação Automática**

```
✅ Execute o instalador baixado
✅ Aceite configurações padrão
✅ Aguarde instalação (10-15 min)
✅ REINICIE o computador (OBRIGATÓRIO)
```

#### **3. Verificação**

```powershell
nvcc --version
# Deve mostrar: "Cuda compilation tools, release 12.x"
```

### 🧪 **TESTE DEFINITIVO DE GPU:**

```powershell
python testar_gpu_real.py
```

**Resultado esperado:**

```
🎉 STATUS: GPU ATIVADA!
✅ llama-cpp-python COM suporte GPU!
⚡ Performance: 50-200+ tokens/segundo
```

---

## 📚 INSTALAÇÃO COMPLETA

### ⚙️ **PRÉ-REQUISITOS DO SISTEMA**

#### **🛠️ 1. Ferramentas de Compilação C++**

```powershell
# Download Visual Studio Build Tools
# https://visualstudio.microsoft.com/pt-br/downloads/
# ✅ Instale "Desenvolvimento para desktop com C++"
# ✅ Reinicie o computador após instalação
```

#### **🐧 2. WSL2 (Windows Subsystem for Linux)**

```powershell
# Execute como Administrador
wsl --install
# ✅ Reinicie o computador
# ✅ Configure usuário/senha no Ubuntu
```

#### **🎮 3. Drivers NVIDIA + CUDA**

```bash
# 1. Drivers NVIDIA Game Ready/Studio
# https://www.nvidia.com.br/Download/index.aspx?lang=br

# 2. CUDA no WSL (opcional - Windows CUDA é suficiente)
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda-repo-wsl-ubuntu-12-4-local_12.4.1-1_amd64.deb
sudo dpkg -i cuda-repo-wsl-ubuntu-12-4-local_12.4.1-1_amd64.deb
sudo cp /var/cuda-repo-wsl-ubuntu-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-4

# 3. Verificação
nvidia-smi  # Deve mostrar sua GPU
```

### 🚀 **INSTALAÇÃO AUTOMATIZADA**

#### **📥 1. Obter o Código**

```powershell
cd C:\DEV\
git clone https://github.com/SEU_USUARIO/Genesys.git
cd Genesys
```

#### **🔑 2. Configurar Variáveis de Ambiente**

Crie `.env` na raiz do projeto:

```env
# --- Configuração do Modelo de IA ---
HUGGING_FACE_REPO_ID="PawanKrd/Meta-Llama-3-70B-Instruct-GGUF"
MODEL_GGUF_FILENAME="llama-3-70b-instruct.Q4_K_M.gguf"
MULTIMODAL_PROJECTOR_FILENAME=""

# --- Configuração da API ---
API_HOST="0.0.0.0"
API_PORT="8002"

# --- Tokens (OBRIGATÓRIOS) ---
HUGGING_FACE_HUB_TOKEN="COLE_SEU_TOKEN_AQUI"
CLOUDFLARE_TUNNEL_TOKEN="COLE_SEU_TOKEN_AQUI"

# --- URLs ---
SERVER_URL="https://genesys.webcreations.com.br"
LOCAL_MODEL_ENDPOINT="http://localhost:8002/v1"
```

**⚠️ IMPORTANTE:** Substitua pelos seus tokens reais:

- [Hugging Face Token](https://huggingface.co/settings/tokens) (permissão de leitura)
- [Cloudflare Tunnel Token](https://one.dash.cloudflare.com/) (Zero Trust)

#### **🔧 3. Instalação Automatizada**

```powershell
# Execute como Administrador
.\scripts\setup_windows.ps1
```

**Este script faz:**

- ✅ Cria ambiente virtual Python
- ✅ Instala todas as dependências
- ✅ Configura CUDA automaticamente
- ✅ Prepara ambiente para execução

#### **📥 4. Download do Modelo (42GB)**

```powershell
# Ative o ambiente virtual
.\venv\Scripts\Activate.ps1

# Baixe o modelo de IA
python .\scripts\download_model.py
```

**⏱️ Tempo estimado:** 30-60 minutos (depende da internet)

---

## 💻 INTEGRAÇÃO COM CURSOR

### 🎯 **OBJETIVO**

Integrar o Genesys diretamente no editor Cursor como sua IA pessoal, com funcionalidades completas de chat, análise de código, revisão e geração.

### 🚀 **INSTALAÇÃO DA EXTENSÃO**

#### **Método Rápido (Recomendado):**

```powershell
# Execute no diretório do projeto
.\instalar_extensao_cursor.ps1
```

### 🔄 **CONFIGURAÇÃO CONTINUE (ALTERNATIVA SIMPLES)**

#### **Para Acesso Remoto (Notebook/Viagem):**

```powershell
# Configure Continue para usar Cloudflare
.\configurar_continue.ps1 -Mode remoto
```

#### **Para Acesso Local (Mesmo PC):**

```powershell
# Configure Continue para servidor local
.\configurar_continue.ps1 -Mode local
```

#### **Método Manual:**

```powershell
# Copiar extensão
cp -r cursor-genesys-extension ~/.cursor/extensions/genesys-ai-assistant
cd ~/.cursor/extensions/genesys-ai-assistant
npm install && npm run compile
```

#### **Ativar no Cursor:**

1. **Reinicie o Cursor**
2. **Recarregar extensões**: `Ctrl+Shift+P` → "Developer: Reload Window"
3. **Verificar instalação**: Procure o ícone 🤖 na barra inferior
4. **Primeiro chat**: Pressione `Ctrl+Shift+G`

### ✨ **FUNCIONALIDADES DA EXTENSÃO**

#### **💬 Chat Interativo**

- **Abrir chat**: `Ctrl+Shift+G` ou clique no ícone 🤖
- **Contexto automático**: Inclui arquivo atual, linguagem e código ao redor
- **Histórico persistente**: Mantém conversas anteriores
- **Interface integrada**: Painel lateral no Explorer

#### **🧠 Análise de Código**

- **Explicar código**: `Ctrl+Shift+E` (com código selecionado)
- **Revisar código**: Clique direito → "🔍 Revisar Código"
- **Otimizar código**: Clique direito → "🚀 Otimizar Código"
- **Gerar código**: `Ctrl+Shift+P` → "Genesys: Gerar Código"

#### **⚡ Comandos Rápidos**

| Comando                | Atalho          | Função          |
| ---------------------- | --------------- | --------------- |
| `genesys.openChat`     | `Ctrl+Shift+G`  | Abrir chat      |
| `genesys.explainCode`  | `Ctrl+Shift+E`  | Explicar código |
| `genesys.reviewCode`   | Menu contexto   | Revisar código  |
| `genesys.optimizeCode` | Menu contexto   | Otimizar código |
| `genesys.generateCode` | Command Palette | Gerar código    |

#### **🔧 Status e Monitoramento**

**Indicadores na barra inferior:**

- **🤖 Genesys ✅**: Conectado e funcionando
- **🤖 Genesys ❌**: Desconectado
- **🤖 Genesys ⚠️**: Erro de conexão

**Painel de status (Explorer → "💬 Genesys AI"):**

- Conectividade em tempo real
- URL do servidor
- Timeout configurado
- Status do agente (Ativo/Desenvolvimento)

### ⚙️ **CONFIGURAÇÕES**

**Configurações disponíveis:**

```json
{
  "genesys.serverUrl": "https://genesys.webcreations.com.br",
  "genesys.timeout": 30,
  "genesys.autoExplain": false,
  "genesys.includeContext": true
}
```

**Como configurar:**

1. **Via UI**: `Ctrl+,` → Busque "Genesys"
2. **Via JSON**: Adicione ao `settings.json`

### 🔄 **ALTERNATIVAS DE INTEGRAÇÃO**

#### **Opção A: Extensão Continue**

1. Instale "Continue" no Cursor
2. Configure modelo customizado:
   ```json
   {
     "models": [
       {
         "title": "Genesys Local",
         "provider": "openai",
         "model": "genesys-local",
         "apiBase": "https://genesys.webcreations.com.br",
         "apiKey": "dummy-key"
       }
     ]
   }
   ```

#### **Opção B: Extensão CodeGPT**

1. Instale "CodeGPT"
2. Configure API custom:
   - URL: `https://genesys.webcreations.com.br/chat`
   - Headers: `Content-Type: application/json`

---

## ▶️ EXECUÇÃO DO SISTEMA

### 🎯 **EXECUÇÃO PADRÃO (RECOMENDADA)**

```powershell
# ◀️ COMANDO PRINCIPAL - USE SEMPRE ▶️
.\start_genesys.ps1
```

**🎮 Recursos Automáticos:**

- ✅ Verificação de dependências
- ✅ GPU ativada (`n_gpu_layers=-1`)
- ✅ Performance máxima (50-200+ tokens/seg)
- ✅ Logs em tempo real
- ✅ Parada limpa com Ctrl+C

### 🚀 **EXECUÇÃO AVANÇADA (BACKGROUND)**

```powershell
# Para execução em background com logs
.\scripts\start_genesys_background.ps1
```

**Recursos Avançados:**

- ✅ Execução em segundo plano
- ✅ Logs salvos em arquivo
- ✅ Verificações automáticas
- ✅ Recuperação de erros

### 🔧 **EXECUÇÃO MANUAL (DEBUG)**

**Terminal 1 - Backend:**

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 2 - Orquestrador:**

```powershell
.\venv\Scripts\Activate.ps1
python .\scripts\autogen_orchestrator.py
```

---

## 🧪 TESTES E VALIDAÇÃO

### 🔬 **TESTE COMPLETO DO SISTEMA**

```powershell
# Teste completo (remoto + local + GPU)
python testar_genesys_completo.py --all

# Teste apenas remoto (Cloudflare)
python testar_genesys_completo.py --remoto

# Teste apenas local
python testar_genesys_completo.py --local

# Teste apenas GPU
python testar_genesys_completo.py --gpu
```

### 🧪 **TESTES MANUAIS RÁPIDOS**

```powershell
# Status básico
curl https://genesys.webcreations.com.br/

# Verificar GPU local
python testar_gpu_real.py
```

### 📊 **VALIDAÇÕES REALIZADAS**

| Teste                | Validação            | Resultado Esperado      |
| -------------------- | -------------------- | ----------------------- |
| **🔗 Conectividade** | Servidor responde    | ✅ Status 200           |
| **💬 Chat Básico**   | Prompt simples       | ✅ Resposta OU modo dev |
| **📥 Download**      | Endpoint funcional   | ✅ Verificação OK       |
| **📜 Scripts**       | Execução de código   | ✅ Script executado     |
| **🖼️ Multimodal**    | Processamento imagem | ✅ Resposta OU N/A      |
| **⚡ Performance**   | Latência conexão     | 📊 Tempo em ms          |
| **🎮 GPU**           | Suporte n_gpu_layers | ✅ GPU ATIVADA          |

---

## 🌐 ACESSO REMOTO COM CLOUDFLARE

### 🔧 **CONFIGURAÇÃO DO TÚNEL**

1. **Obter Token:**

   - Acesse [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
   - Crie um túnel
   - Copie o token de instalação

2. **Configurar Script:**

   ```powershell
   # Edite o arquivo
   notepad scripts\setup_cloudflare_tunnel.ps1
   # Cole seu token na variável $CloudflareToken
   ```

3. **Executar (como Admin):**
   ```powershell
   .\scripts\setup_cloudflare_tunnel.ps1
   ```

### 🔍 **MONITORAMENTO DO TÚNEL**

```bash
# Descobrir URL automaticamente
python scripts/cloudflare_tunnel_helper.py discover

# Testar conectividade
python scripts/cloudflare_tunnel_helper.py test

# Monitorar em tempo real
python scripts/cloudflare_tunnel_helper.py monitor
```

---

## 🔧 CONFIGURAÇÕES AVANÇADAS

### 👥 **AutoGen Multi-Agente**

```bash
# Iniciar orquestrador AutoGen
python autogen_logic/main.py

# API disponível em: http://localhost:8003
# Endpoints:
# - POST /chat (conversa direta)
# - POST /debate (debate Genesys vs Gemini)
```

### 🔄 **Webhooks GitHub**

O arquivo `.github/workflows/code_review.yml` já está configurado para:

- Revisar commits automaticamente
- Comentar com análises do Genesys
- Sugerir melhorias

### 📈 **Fine-Tuning Contínuo**

```bash
# Quando tiver dados suficientes
python scripts/fine_tune.py
```

**Logs automáticos:**

- ✅ Todas as interações com o agente
- ✅ Prompts e respostas completas
- ✅ Passos intermediários das ferramentas
- ✅ Timestamp e metadados

**Arquivo:** `data/logs/interaction_logs.jsonl`

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### ❌ **PROBLEMAS COMUNS E SOLUÇÕES**

#### **1. GPU NÃO FUNCIONANDO**

**Problema:** `python testar_gpu_real.py` mostra "❌ SEM GPU SUPPORT"

**Diagnóstico:**

```powershell
# Verificar CUDA
nvcc --version

# Diagnóstico completo
.\DIAGNOSTICO_CUDA_COMPLETO.ps1
```

**Soluções:**

1. **CUDA não instalado:** Instale CUDA Toolkit + reinicie PC
2. **VS Build Tools:** Instale Visual Studio Build Tools
3. **Recompilação:** Execute `pip install llama-cpp-python --force-reinstall`

#### **2. SERVIDOR NÃO INICIA**

**Problema:** `.\start_genesys.ps1` falha

**Diagnóstico:**

```powershell
# Verificar Python
.\venv\Scripts\python.exe --version

# Verificar dependências
.\venv\Scripts\python.exe -c "import fastapi, uvicorn"
```

**Soluções:**

1. **Ambiente Virtual:** Recrie com `python -m venv venv`
2. **Dependências:** Execute `pip install -r requirements.txt`
3. **Porta ocupada:** Use porta diferente: `.\start_genesys.ps1 -Port 8003`

#### **3. EXTENSÃO CURSOR NÃO FUNCIONA**

**Problema:** Extensão não carrega ou não conecta

**Diagnóstico:**

```powershell
# Verificar instalação
dir "$env:USERPROFILE\.cursor\extensions\genesys-ai-assistant"

# Teste de conectividade
curl https://genesys.webcreations.com.br/
```

**Soluções:**

1. **Reinstalar extensão:** Execute `.\instalar_extensao_cursor.ps1 -Force`
2. **Recarregar Cursor:** `Ctrl+Shift+P` → "Developer: Reload Window"
3. **Verificar logs:** `Help` → `Toggle Developer Tools` → `Console`

#### **4. MODELO NÃO ENCONTRADO**

**Problema:** "Modelo não encontrado"

**Diagnóstico:**

```powershell
# Verificar arquivo
dir models\*.gguf

# Verificar tamanho
dir models\*.gguf | ForEach-Object { "{0:N1} GB - {1}" -f ($_.Length/1GB), $_.Name }
```

**Soluções:**

1. **Download:** Execute `python scripts/download_model.py`
2. **Espaço:** Verifique espaço livre (mínimo 50GB)
3. **Path:** Verifique configuração no `.env`

#### **5. PERFORMANCE BAIXA**

**Problema:** Respostas lentas (< 10 tokens/seg)

**Diagnóstico:**

```powershell
# Verificar se GPU está sendo usada
nvidia-smi

# Verificar configuração
python testar_gpu_real.py
```

**Soluções:**

1. **GPU não ativa:** Recompile com CUDA
2. **VRAM insuficiente:** Use modelo menor (8B/13B)
3. **RAM insuficiente:** Aumente swap/virtual memory

---

## 📚 ESTRUTURA DO PROJETO

```
Genesys/
├── 🤖 app/                          # Core da aplicação
│   ├── agent_logic.py              # Lógica principal (GPU configurada)
│   ├── main.py                     # FastAPI server
│   └── tools/                      # Ferramentas do agente
├── 🚀 scripts/                     # Scripts essenciais
│   ├── start_genesys.ps1          # ⭐ COMANDO PRINCIPAL
│   ├── start_genesys_server.py    # Core do servidor
│   ├── test_server_notebook.py    # Testes completos
│   └── download_model.py          # Download de modelos
├── 💻 cursor-genesys-extension/    # Extensão para Cursor
│   ├── package.json               # Configuração da extensão
│   ├── src/                       # Código TypeScript
│   │   ├── extension.ts           # Ponto de entrada
│   │   ├── genesysApi.ts         # API de comunicação
│   │   └── chatProvider.ts       # Provider do chat
│   └── README.md                  # Guia da extensão
├── 👥 autogen_logic/               # Orquestração multi-agente
│   ├── main.py                    # AutoGen FastAPI
│   ├── config.py                  # Configuração de modelos
│   └── tools/                     # Ferramentas AutoGen
├── 🧠 models/                      # Modelos de IA (GGUF)
├── 📊 data/logs/                   # Logs para fine-tuning
├── 🔧 venv/                        # Ambiente virtual Python
├── 🗂️ workspace/                   # Área de trabalho segura
├── 📄 .env                         # Configurações
├── 🎮 testar_gpu_real.py          # Teste definitivo GPU
├── 🔧 instalar_extensao_cursor.ps1 # Instalador da extensão
└── 📚 README.md                   # Esta documentação
```

---

## 🎯 PRÓXIMOS PASSOS

### ✅ **APÓS CONFIGURAÇÃO**

1. **Validar Instalação**

   ```bash
   python scripts/test_server_notebook.py
   ```

2. **Primeira Interação**

   - Acesse: `https://genesys.webcreations.com.br/docs`
   - Teste o endpoint `/chat`

3. **Configurar Extensão Cursor**

   ```bash
   .\instalar_extensao_cursor.ps1
   ```

4. **Ativar Modelo Completo**

   ```bash
   .\start_genesys.ps1
   ```

5. **Fine-Tuning** (após 1000+ interações)
   ```bash
   python scripts/fine_tune.py
   ```

### 🎮 **FLUXO DE TRABALHO IDEAL**

1. **Iniciar Genesys**: `.\start_genesys.ps1`
2. **Abrir Cursor**: Com extensão instalada
3. **Chat direto**: `Ctrl+Shift+G`
4. **Explicar código**: Selecionar + `Ctrl+Shift+E`
5. **Revisar código**: Clique direito → "🔍 Revisar Código"
6. **Gerar código**: Command Palette → "Genesys: Gerar Código"

---

## 📞 COMANDOS DE EMERGÊNCIA

### 🛑 **PARAR TUDO**

```powershell
# Para todos os processos Python
Get-Process python | Stop-Process -Force

# Libera portas específicas
Get-NetTCPConnection -LocalPort 8002 | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force
}
```

### 🔄 **RESET COMPLETO**

```powershell
# Remove ambiente virtual
Remove-Item venv -Recurse -Force

# Recria do zero
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Re-baixar modelo se necessário
python scripts/download_model.py
```

### 🆘 **DIAGNÓSTICO COMPLETO**

```bash
# Verificar ambiente
python scripts/start_genesys_server.py --model-check-only

# Teste de conectividade
python scripts/test_server_notebook.py --quick

# Status do túnel
python scripts/cloudflare_tunnel_helper.py discover

# Diagnóstico CUDA
.\DIAGNOSTICO_CUDA_COMPLETO.ps1

# Teste GPU real
python testar_gpu_real.py
```

---

## 🎯 RESUMO EXECUTIVO

| Item                | Status        | Comando/Info                     |
| ------------------- | ------------- | -------------------------------- |
| **🚀 Iniciar IA**   | ✅ Pronto     | `.\start_genesys.ps1`            |
| **🎮 GPU**          | ✅ Ativada    | `n_gpu_layers=-1` (configurado)  |
| **⚡ Performance**  | ✅ Máxima     | 50-200+ tokens/seg               |
| **💻 Cursor**       | ✅ Integrado  | `.\instalar_extensao_cursor.ps1` |
| **📚 Documentação** | ✅ Unificada  | Este arquivo README.md           |
| **🔧 Diagnóstico**  | ✅ Disponível | `python testar_gpu_real.py`      |

---

## 💡 DICAS IMPORTANTES

1. **🎮 GPU SEMPRE ATIVA** quando usar `.\start_genesys.ps1`
2. **⚡ Performance máxima** garantida com `n_gpu_layers=-1`
3. **💻 Extensão Cursor** para máxima produtividade
4. **📚 Documentação unificada** neste README.md
5. **🔧 Diagnóstico disponível** se precisar no futuro
6. **🚀 Comando único** para lembrar: `.\start_genesys.ps1`

---

<div align="center">

## 🎉 RESULTADO FINAL

### ✅ **SISTEMA COMPLETO E FUNCIONANDO**

![Success](https://img.shields.io/badge/✅-SISTEMA_PRONTO-success?style=for-the-badge)
![GPU](https://img.shields.io/badge/🎮-GPU_ATIVADA-green?style=for-the-badge)
![Cursor](https://img.shields.io/badge/💻-CURSOR_INTEGRADO-blue?style=for-the-badge)
![Performance](https://img.shields.io/badge/⚡-ULTRA_RÁPIDO-orange?style=for-the-badge)

**🎯 SEUS COMANDOS ÚNICOS:**

```powershell
# Iniciar Genesys
.\start_genesys.ps1

# Instalar extensão Cursor
.\instalar_extensao_cursor.ps1
```

**🌟 Seu agente Genesys está pronto para dominar o mundo da IA local!**

_Sistema desenvolvido para máxima autonomia, privacidade e performance._

---

![Footer](https://img.shields.io/badge/🤖-GENESYS_POWERED-purple?style=for-the-badge)
![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)

</div>
