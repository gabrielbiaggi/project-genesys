# scripts/start_genesys_background.ps1
<#
.SYNOPSIS
    Inicia o servidor Genesys em segundo plano mantendo a saída visível.

.DESCRIPTION
    Este script resolve o problema de executar o servidor em background no Windows,
    usando PowerShell jobs e redirecionamento para manter os logs visíveis.

.PARAMETER Port
    Porta do servidor (padrão: 8002)

.PARAMETER Host  
    Host do servidor (padrão: 0.0.0.0)

.PARAMETER LogFile
    Arquivo de log (padrão: genesys_server.log)

.EXAMPLE
    .\scripts\start_genesys_background.ps1
    .\scripts\start_genesys_background.ps1 -Port 8003 -LogFile "custom.log"
#>

param(
    [int]$Port = 8002,
    [string]$Host = "0.0.0.0", 
    [string]$LogFile = "genesys_server.log"
)

# Configurações
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$VenvPath = Join-Path $ProjectRoot "venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$LogPath = Join-Path $ProjectRoot $LogFile

# Função para escrever mensagens coloridas
function Write-GenesysMessage {
    param([string]$Message, [string]$Color = "White")
    Write-Host "🤖 GENESYS: $Message" -ForegroundColor $Color
}

# Função para verificar se o ambiente virtual existe
function Test-VirtualEnvironment {
    if (-not (Test-Path $PythonExe)) {
        Write-GenesysMessage "Ambiente virtual não encontrado em: $VenvPath" "Red"
        Write-GenesysMessage "Execute: python -m venv venv && .\venv\Scripts\Activate.ps1 && pip install -r requirements.txt" "Yellow"
        return $false
    }
    return $true
}

# Função para instalar dependências faltantes
function Install-MissingDependencies {
    Write-GenesysMessage "Verificando e instalando dependências faltantes..." "Cyan"
    
    $RequiredModules = @("psutil", "fastapi", "uvicorn", "langchain")
    
    foreach ($Module in $RequiredModules) {
        try {
            $Result = & $PythonExe -c "import $($Module.Replace('-', '_')); print('OK')" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-GenesysMessage "$Module - ✅ OK" "Green"
            } else {
                throw "Módulo não encontrado"
            }
        } catch {
            Write-GenesysMessage "$Module - ❌ INSTALANDO..." "Yellow"
            & $PythonExe -m pip install $Module
            if ($LASTEXITCODE -eq 0) {
                Write-GenesysMessage "$Module - ✅ INSTALADO" "Green"
            } else {
                Write-GenesysMessage "$Module - ❌ FALHA NA INSTALAÇÃO" "Red"
                return $false
            }
        }
    }
    return $true
}

# Função para verificar se a porta está disponível
function Test-PortAvailability {
    param([int]$TestPort)
    
    try {
        $Connection = Get-NetTCPConnection -LocalPort $TestPort -ErrorAction SilentlyContinue
        if ($Connection) {
            Write-GenesysMessage "Porta $TestPort já está em uso" "Red"
            return $false
        }
        Write-GenesysMessage "Porta $TestPort disponível" "Green"
        return $true
    } catch {
        Write-GenesysMessage "Porta $TestPort disponível" "Green"
        return $true
    }
}

# Função para parar processos existentes do Genesys
function Stop-ExistingGenesys {
    Write-GenesysMessage "Verificando processos existentes do Genesys..." "Cyan"
    
    $GenesysProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
        $_.CommandLine -like "*genesys*" -or $_.CommandLine -like "*uvicorn*app.main*"
    }
    
    if ($GenesysProcesses) {
        Write-GenesysMessage "Parando $($GenesysProcesses.Count) processo(s) existente(s)..." "Yellow"
        $GenesysProcesses | Stop-Process -Force
        Start-Sleep -Seconds 3
        Write-GenesysMessage "Processos existentes parados" "Green"
    } else {
        Write-GenesysMessage "Nenhum processo existente encontrado" "Green"
    }
}

# Função principal para iniciar o servidor
function Start-GenesysBackground {
    Write-GenesysMessage "Iniciando servidor Genesys em background..." "Cyan"
    
    # Comando para iniciar o servidor
    $ServerCommand = @(
        $PythonExe,
        "scripts\start_genesys_server.py",
        "--port", $Port,
        "--host", $Host
    )
    
    # Inicia o processo em background usando Start-Process
    $ProcessParams = @{
        FilePath = $PythonExe
        ArgumentList = "scripts\start_genesys_server.py", "--port", $Port, "--host", $Host
        WorkingDirectory = $ProjectRoot
        RedirectStandardOutput = $LogPath
        RedirectStandardError = $LogPath
        PassThru = $true
        WindowStyle = "Hidden"
    }
    
    try {
        $ServerProcess = Start-Process @ProcessParams
        
        Write-GenesysMessage "Servidor iniciado com PID: $($ServerProcess.Id)" "Green"
        Write-GenesysMessage "Logs sendo salvos em: $LogPath" "Cyan"
        Write-GenesysMessage "Monitorando logs em tempo real... (Ctrl+C para parar o monitoramento)" "Yellow"
        
        # Aguarda um pouco para o servidor inicializar
        Start-Sleep -Seconds 5
        
        # Verifica se o processo ainda está rodando
        if (-not $ServerProcess.HasExited) {
            Write-GenesysMessage "✅ Servidor rodando em background!" "Green"
            Write-GenesysMessage "🌐 URL Local: http://localhost:$Port" "Cyan"
            Write-GenesysMessage "🌍 URL Túnel: https://genesys.webcreations.com.br" "Cyan"
            Write-GenesysMessage "📚 Documentação: http://localhost:$Port/docs" "Cyan"
            
            # Retorna informações do processo
            return @{
                Process = $ServerProcess
                PID = $ServerProcess.Id
                LogFile = $LogPath
                Port = $Port
            }
        } else {
            Write-GenesysMessage "❌ Servidor falhou ao iniciar" "Red"
            return $null
        }
        
    } catch {
        Write-GenesysMessage "❌ Erro ao iniciar servidor: $($_.Exception.Message)" "Red"
        return $null
    }
}

# Função para monitorar logs em tempo real
function Watch-GenesysLogs {
    param([string]$LogFilePath)
    
    if (-not (Test-Path $LogFilePath)) {
        Write-GenesysMessage "Aguardando criação do arquivo de log..." "Yellow"
        while (-not (Test-Path $LogFilePath)) {
            Start-Sleep -Seconds 1
        }
    }
    
    try {
        # Usa Get-Content com -Wait para monitorar em tempo real
        Write-GenesysMessage "Monitorando logs (pressione Ctrl+C para parar):" "Cyan"
        Write-Host ("-" * 80) -ForegroundColor Gray
        
        Get-Content $LogFilePath -Wait | ForEach-Object {
            $Timestamp = Get-Date -Format "HH:mm:ss"
            Write-Host "[$Timestamp] $_" -ForegroundColor White
        }
        
    } catch {
        if ($_.Exception.Message -notlike "*interrupted*") {
            Write-GenesysMessage "Erro ao monitorar logs: $($_.Exception.Message)" "Red"
        }
    }
}

# Função para salvar informações do processo
function Save-ProcessInfo {
    param($ProcessInfo)
    
    if ($ProcessInfo) {
        $InfoFile = Join-Path $ProjectRoot ".genesys_process_info.json"
        $ProcessData = @{
            PID = $ProcessInfo.PID
            Port = $ProcessInfo.Port  
            LogFile = $ProcessInfo.LogFile
            StartTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        } | ConvertTo-Json
        
        $ProcessData | Out-File -FilePath $InfoFile -Encoding UTF8
        Write-GenesysMessage "Informações do processo salvas em: $InfoFile" "Green"
    }
}

# SCRIPT PRINCIPAL
Clear-Host
Write-Host "🚀 GENESYS BACKGROUND STARTER" -ForegroundColor Magenta
Write-Host ("=" * 60) -ForegroundColor Gray
Write-Host "📁 Projeto: $ProjectRoot" -ForegroundColor Cyan
Write-Host "🐍 Python: $PythonExe" -ForegroundColor Cyan  
Write-Host "🌐 Servidor: ${Host}:${Port}" -ForegroundColor Cyan
Write-Host "📄 Log: $LogPath" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

try {
    # Passo 1: Verificar ambiente virtual
    if (-not (Test-VirtualEnvironment)) {
        exit 1
    }
    
    # Passo 2: Instalar dependências faltantes
    if (-not (Install-MissingDependencies)) {
        Write-GenesysMessage "Falha ao instalar dependências" "Red"
        exit 1
    }
    
    # Passo 3: Verificar porta
    if (-not (Test-PortAvailability -TestPort $Port)) {
        Write-GenesysMessage "Porta não disponível. Tente uma porta diferente com -Port XXXX" "Red"
        exit 1
    }
    
    # Passo 4: Parar processos existentes
    Stop-ExistingGenesys
    
    # Passo 5: Iniciar servidor em background
    $ProcessInfo = Start-GenesysBackground
    
    if ($ProcessInfo) {
        # Salva informações do processo
        Save-ProcessInfo -ProcessInfo $ProcessInfo
        
        # Monitora logs em tempo real
        Watch-GenesysLogs -LogFilePath $ProcessInfo.LogFile
    } else {
        Write-GenesysMessage "Falha ao iniciar o servidor" "Red"
        exit 1
    }
    
} catch {
    Write-GenesysMessage "Erro inesperado: $($_.Exception.Message)" "Red"
    exit 1
} finally {
    Write-GenesysMessage "Script finalizado" "Gray"
}