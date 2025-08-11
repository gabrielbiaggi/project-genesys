# 🚀 GUIA COMPLETO - GENESYS COMO SERVIÇO WINDOWS

## 🎯 **VISÃO GERAL**

O Genesys agora pode rodar como um **serviço nativo do Windows** usando NSSM, garantindo:

- ✅ **Execução independente** do terminal
- ✅ **Início automático** com o Windows  
- ✅ **Reinicialização automática** em caso de falha
- ✅ **Monitoramento independente** 
- ✅ **Logs centralizados**

---

## 🚀 **COMANDO PRINCIPAL (NOVO)**

### **⚡ Uso Básico:**

```powershell
# Comando MASTER - detecta e inicia automaticamente
.\iniciar_genesys.ps1

# Forçar modo serviço + monitor
.\iniciar_genesys.ps1 -Service -Monitor

# Ver status completo
.\iniciar_genesys.ps1 -Action status
```

### **🧠 Detecção Inteligente:**

O comando principal agora **detecta automaticamente**:
- ✅ Se o serviço está instalado
- ✅ Se está rodando
- ✅ Se a API está respondendo  
- ✅ Inicia automaticamente o que for necessário

---

## 🔧 **INSTALAÇÃO DO SERVIÇO**

### **📦 Instalação Automática:**

```powershell
# Execute como Administrador
.\iniciar_genesys.ps1 -Action install
```

**O que acontece:**
1. ✅ Baixa e instala **NSSM** automaticamente
2. ✅ Cria serviço **"GenesysAI"**
3. ✅ Configura **início automático**
4. ✅ Define **logs centralizados**
5. ✅ Configura **reinicialização automática**

### **⚙️ Instalação Manual (se necessário):**

```powershell
# Instalar NSSM primeiro (se não baixar automaticamente)
# Baixe de: https://nssm.cc/download
# Extraia para C:\Program Files\NSSM\

# Depois instalar serviço
.\scripts\setup_genesys_service.ps1 -Action install
```

---

## 🎮 **COMANDOS DE GERENCIAMENTO**

### **🚀 Controle Básico:**

```powershell
# Iniciar (detecta e inicia automaticamente)
.\iniciar_genesys.ps1

# Parar serviço
.\iniciar_genesys.ps1 -Action stop

# Reiniciar serviço
.\iniciar_genesys.ps1 -Action restart

# Ver status detalhado
.\iniciar_genesys.ps1 -Action status
```

### **🔧 Gerenciamento Avançado:**

```powershell
# Remover serviço (execute como Admin)
.\iniciar_genesys.ps1 -Action remove

# Instalação com porta customizada
.\iniciar_genesys.ps1 -Action install -Port 8003

# Modo manual (compatibilidade)
.\iniciar_genesys.ps1 -Action manual
```

---

## 📊 **SISTEMA DE MONITORAMENTO**

### **🖥️ Monitor Interativo:**

```powershell
# Monitor com interface visual
.\iniciar_genesys.ps1 -Action monitor

# Iniciar com monitor automático
.\iniciar_genesys.ps1 -Monitor
```

**Características:**
- ✅ **Interface visual** em tempo real
- ✅ **Status do serviço** Windows
- ✅ **Status da API** local e remota
- ✅ **Métricas de performance**
- ✅ **Detecção de problemas**

### **🔄 Monitor Background:**

```powershell
# Monitor em background (sem interface)
.\iniciar_genesys.ps1 -Monitor -Background

# Ou diretamente:
python scripts\monitor_genesys_independente.py --background
```

**Características:**
- ✅ **Execução silenciosa**
- ✅ **Reinicialização automática** do serviço
- ✅ **Logs de atividade**
- ✅ **Independente do terminal**

---

## 📁 **ESTRUTURA DE ARQUIVOS**

### **🔧 Scripts Principais:**

```
📂 scripts/
├── 🚀 setup_genesys_service.ps1      # Gerenciador do serviço NSSM
├── 🤖 genesys_service_runner.py      # Runner otimizado para serviço
├── 📊 monitor_genesys_independente.py # Monitor independente
└── 📁 outros scripts...

📂 raiz/
├── ⚡ iniciar_genesys.ps1            # COMANDO PRINCIPAL (NOVO)
└── 🔄 start_genesys.ps1              # Modo manual (compatibilidade)
```

### **📋 Logs Centralizados:**

```
📂 data/logs/
├── 📝 genesys_service.log            # Logs do serviço Windows
├── 🌐 uvicorn_service.log            # Logs da API
├── 📊 monitor_stats.json             # Estatísticas do monitor
└── 🧠 training_system.log            # Logs do sistema de treinamento
```

---

## 🎯 **FLUXOS DE USO**

### **🆕 Primeira Vez (Setup Completo):**

```powershell
# 1. Execute como Administrador
.\iniciar_genesys.ps1 -Action install

# 2. Inicie o serviço + monitor
.\iniciar_genesys.ps1 -Service -Monitor

# 3. Teste conectividade
curl http://localhost:8002/
```

### **📅 Uso Diário:**

```powershell
# Comando único - detecta tudo automaticamente
.\iniciar_genesys.ps1

# Verificar se está tudo OK
.\iniciar_genesys.ps1 -Action status
```

### **🔧 Manutenção:**

```powershell
# Reiniciar se houver problemas
.\iniciar_genesys.ps1 -Action restart

# Ver logs em tempo real
Get-Content data\logs\genesys_service.log -Wait -Tail 10

# Monitor para diagnóstico
.\iniciar_genesys.ps1 -Action monitor
```

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **❌ Serviço não inicia:**

```powershell
# 1. Verificar pré-requisitos
python --version
.\venv\Scripts\python.exe -c "import fastapi"

# 2. Verificar logs
Get-Content data\logs\genesys_service.log -Tail 20

# 3. Reinstalar se necessário (como Admin)
.\iniciar_genesys.ps1 -Action remove
.\iniciar_genesys.ps1 -Action install
```

### **⚠️ API não responde:**

```powershell
# 1. Verificar se serviço está rodando
.\iniciar_genesys.ps1 -Action status

# 2. Aguardar carregamento do modelo (pode levar 2-5 min)
# 3. Verificar firewall/antivírus na porta 8002

# 4. Testar com monitor
.\iniciar_genesys.ps1 -Action monitor
```

### **🔄 Erro de permissão:**

```powershell
# Execute PowerShell como Administrador
# Clique direito → "Executar como administrador"

# Ou configure policy (como Admin):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📈 **VANTAGENS DO SERVIÇO**

### **🎯 Vs. Execução Manual:**

| Característica | Manual | **Serviço** |
|---------------|--------|------------|
| **Independência do terminal** | ❌ | ✅ |
| **Início automático** | ❌ | ✅ |
| **Reinício automático** | ❌ | ✅ |
| **Logs centralizados** | ❌ | ✅ |
| **Gerenciamento Windows** | ❌ | ✅ |
| **Performance** | ⚡ | ⚡ |

### **💡 Benefícios Práticos:**

- ✅ **Servidor sempre disponível** (24/7)
- ✅ **Sobrevive a desconexões** RDP/SSH
- ✅ **Reinicia com o Windows**
- ✅ **Logs organizados** e persistentes
- ✅ **Monitoramento independente**
- ✅ **Integração nativa** com Windows

---

## 🎮 **COMANDOS RÁPIDOS DE REFERÊNCIA**

```powershell
# === ESSENCIAIS ===
.\iniciar_genesys.ps1                    # Detecta e inicia tudo
.\iniciar_genesys.ps1 -Action status     # Status completo
.\iniciar_genesys.ps1 -Action monitor    # Monitor visual

# === GERENCIAMENTO ===
.\iniciar_genesys.ps1 -Action install    # Instalar (como Admin)
.\iniciar_genesys.ps1 -Action restart    # Reiniciar serviço
.\iniciar_genesys.ps1 -Action remove     # Remover (como Admin)

# === MONITORAMENTO ===
.\iniciar_genesys.ps1 -Monitor           # Iniciar com monitor
.\iniciar_genesys.ps1 -Monitor -Background # Monitor em background

# === COMPATIBILIDADE ===
.\iniciar_genesys.ps1 -Action manual     # Modo terminal tradicional
.\start_genesys.ps1                      # Script antigo (funciona)
```

---

## 🌟 **PRÓXIMAS MELHORIAS**

- 🔜 **Interface web** para gerenciamento
- 🔜 **Alertas por email** em caso de problemas  
- 🔜 **Backup automático** de configurações
- 🔜 **Deploy automatizado** de atualizações
- 🔜 **Dashboard em tempo real**

**🎯 O Genesys agora é um serviço profissional do Windows, rodando de forma robusta e independente!**
