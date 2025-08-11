# scripts/setup_genesys_service.ps1
# Script para configurar Genesys como serviço do Windows usando NSSM

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("install", "remove", "start", "stop", "restart", "status")]
    [string]$Action = "install",
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "GenesysAI",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8002,
    
    [Parameter(Mandatory=$false)]
    [string]$Host = "0.0.0.0"
)

# Configurações
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot "venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$ServiceScript = Join-Path $ProjectRoot "scripts\genesys_service_runner.py"
$LogsDir = Join-Path $ProjectRoot "data\logs"
$ServiceLog = Join-Path $LogsDir "genesys_service.log"
$NSSMPath = "nssm"  # Assumindo que NSSM está no PATH

Write-Host "🚀 CONFIGURADOR DE SERVIÇO GENESYS" -ForegroundColor Cyan
Write-Host "=" * 50
Write-Host "Ação: $Action" -ForegroundColor Yellow
Write-Host "Serviço: $ServiceName" -ForegroundColor White
Write-Host ""

# Verificar se está executando como administrador
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Host "❌ ERRO: Este script deve ser executado como Administrador!" -ForegroundColor Red
    Write-Host "💡 Clique com botão direito no PowerShell → 'Executar como administrador'" -ForegroundColor Yellow
    exit 1
}

# Verificar se NSSM está disponível
function Test-NSSM {
    try {
        $null = Get-Command $NSSMPath -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Baixar e instalar NSSM se necessário
function Install-NSSM {
    if (Test-NSSM) {
        Write-Host "✅ NSSM já está disponível" -ForegroundColor Green
        return $true
    }
    
    Write-Host "📥 NSSM não encontrado. Instalando..." -ForegroundColor Yellow
    
    $NSSMUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $TempDir = $env:TEMP
    $NSSMZip = Join-Path $TempDir "nssm.zip"
    $NSSMExtract = Join-Path $TempDir "nssm"
    $ProgramFiles = ${env:ProgramFiles}
    $NSSMInstallDir = Join-Path $ProgramFiles "NSSM"
    
    try {
        # Download NSSM
        Write-Host "📥 Baixando NSSM..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $NSSMUrl -OutFile $NSSMZip -UseBasicParsing
        
        # Extrair
        Write-Host "📦 Extraindo NSSM..." -ForegroundColor Yellow
        Expand-Archive -Path $NSSMZip -DestinationPath $NSSMExtract -Force
        
        # Instalar
        Write-Host "📁 Instalando NSSM..." -ForegroundColor Yellow
        $NSSMSource = Get-ChildItem -Path $NSSMExtract -Recurse -Name "nssm.exe" | Select-Object -First 1
        $NSSMSourcePath = Join-Path $NSSMExtract $NSSMSource
        
        if (-not (Test-Path $NSSMInstallDir)) {
            New-Item -ItemType Directory -Path $NSSMInstallDir -Force | Out-Null
        }
        
        Copy-Item -Path (Split-Path $NSSMSourcePath) -Destination $NSSMInstallDir -Recurse -Force
        
        # Adicionar ao PATH
        $CurrentPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::Machine)
        if ($CurrentPath -notlike "*$NSSMInstallDir*") {
            $NewPath = "$CurrentPath;$NSSMInstallDir\win64"
            [Environment]::SetEnvironmentVariable("PATH", $NewPath, [EnvironmentVariableTarget]::Machine)
        }
        
        # Atualizar PATH da sessão atual
        $env:PATH += ";$NSSMInstallDir\win64"
        $script:NSSMPath = Join-Path $NSSMInstallDir "win64\nssm.exe"
        
        # Cleanup
        Remove-Item $NSSMZip -Force -ErrorAction SilentlyContinue
        Remove-Item $NSSMExtract -Recurse -Force -ErrorAction SilentlyContinue
        
        Write-Host "✅ NSSM instalado com sucesso!" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "❌ Erro ao instalar NSSM: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Verificar pré-requisitos
function Test-Prerequisites {
    Write-Host "🔍 Verificando pré-requisitos..." -ForegroundColor Yellow
    
    # Verificar Python
    if (-not (Test-Path $PythonExe)) {
        Write-Host "❌ Python não encontrado em: $PythonExe" -ForegroundColor Red
        Write-Host "💡 Execute primeiro: .\scripts\setup_windows.ps1" -ForegroundColor Yellow
        return $false
    }
    
    # Verificar FastAPI
    try {
        & $PythonExe -c "import fastapi, uvicorn" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Dependências Python não encontradas" -ForegroundColor Red
            Write-Host "💡 Execute: .\venv\Scripts\Activate.ps1; pip install -r requirements.txt" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Erro ao verificar dependências Python" -ForegroundColor Red
        return $false
    }
    
    # Verificar logs directory
    if (-not (Test-Path $LogsDir)) {
        New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    }
    
    Write-Host "✅ Pré-requisitos verificados com sucesso!" -ForegroundColor Green
    return $true
}

# Instalar serviço
function Install-GenesysService {
    Write-Host "🔧 INSTALANDO SERVIÇO GENESYS" -ForegroundColor Cyan
    Write-Host "-" * 40
    
    # Verificar se serviço já existe
    $ExistingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($ExistingService) {
        Write-Host "⚠️ Serviço '$ServiceName' já existe!" -ForegroundColor Yellow
        Write-Host "💡 Use: -Action remove para remover primeiro" -ForegroundColor Yellow
        return $false
    }
    
    # Criar argumentos do serviço
    $ServiceArgs = @(
        $ServiceScript,
        "--host", $Host,
        "--port", $Port
    )
    
    try {
        # Instalar serviço com NSSM
        Write-Host "📦 Criando serviço com NSSM..." -ForegroundColor Yellow
        & $NSSMPath install $ServiceName $PythonExe $ServiceArgs
        
        # Configurar serviço
        Write-Host "⚙️ Configurando serviço..." -ForegroundColor Yellow
        
        # Diretório de trabalho
        & $NSSMPath set $ServiceName AppDirectory $ProjectRoot
        
        # Logs
        & $NSSMPath set $ServiceName AppStdout $ServiceLog
        & $NSSMPath set $ServiceName AppStderr $ServiceLog
        
        # Configurações de execução
        & $NSSMPath set $ServiceName DisplayName "Genesys AI Server"
        & $NSSMPath set $ServiceName Description "Servidor de IA Genesys com LLaVA 70B"
        & $NSSMPath set $ServiceName Start SERVICE_AUTO_START
        
        # Configurações de falha
        & $NSSMPath set $ServiceName AppRestartDelay 5000
        & $NSSMPath set $ServiceName AppStopMethodSkip 0
        & $NSSMPath set $ServiceName AppStopMethodConsole 1500
        & $NSSMPath set $ServiceName AppStopMethodWindow 1500
        & $NSSMPath set $ServiceName AppStopMethodThreads 1500
        & $NSSMPath set $ServiceName AppKillProcessTree 1
        
        Write-Host "✅ Serviço '$ServiceName' instalado com sucesso!" -ForegroundColor Green
        Write-Host "🎯 Para iniciar: -Action start" -ForegroundColor Cyan
        return $true
        
    } catch {
        Write-Host "❌ Erro ao instalar serviço: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Remover serviço
function Remove-GenesysService {
    Write-Host "🗑️ REMOVENDO SERVIÇO GENESYS" -ForegroundColor Red
    Write-Host "-" * 40
    
    try {
        # Parar serviço se estiver rodando
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($Service -and $Service.Status -eq "Running") {
            Write-Host "⏹️ Parando serviço..." -ForegroundColor Yellow
            Stop-Service -Name $ServiceName -Force
            Start-Sleep 3
        }
        
        # Remover com NSSM
        Write-Host "🗑️ Removendo serviço..." -ForegroundColor Yellow
        & $NSSMPath remove $ServiceName confirm
        
        Write-Host "✅ Serviço '$ServiceName' removido com sucesso!" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "❌ Erro ao remover serviço: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Iniciar serviço
function Start-GenesysService {
    Write-Host "▶️ INICIANDO SERVIÇO GENESYS" -ForegroundColor Green
    Write-Host "-" * 40
    
    try {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if (-not $Service) {
            Write-Host "❌ Serviço '$ServiceName' não está instalado!" -ForegroundColor Red
            Write-Host "💡 Use: -Action install para instalar primeiro" -ForegroundColor Yellow
            return $false
        }
        
        if ($Service.Status -eq "Running") {
            Write-Host "✅ Serviço já está rodando!" -ForegroundColor Green
            return $true
        }
        
        Write-Host "🚀 Iniciando serviço..." -ForegroundColor Yellow
        Start-Service -Name $ServiceName
        
        # Aguardar inicialização
        Write-Host "⏳ Aguardando inicialização..." -ForegroundColor Yellow
        Start-Sleep 5
        
        # Verificar status
        $Service = Get-Service -Name $ServiceName
        if ($Service.Status -eq "Running") {
            Write-Host "✅ Serviço iniciado com sucesso!" -ForegroundColor Green
            
            # Testar conectividade
            Write-Host "🧪 Testando conectividade..." -ForegroundColor Yellow
            Start-Sleep 3
            
            try {
                $Response = Invoke-WebRequest -Uri "http://localhost:$Port/" -UseBasicParsing -TimeoutSec 10
                if ($Response.StatusCode -eq 200) {
                    Write-Host "✅ Servidor respondendo na porta $Port!" -ForegroundColor Green
                } else {
                    Write-Host "⚠️ Servidor iniciado mas não respondendo corretamente" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "⚠️ Servidor pode estar carregando. Aguarde alguns minutos." -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ Falha ao iniciar serviço!" -ForegroundColor Red
            return $false
        }
        
        return $true
        
    } catch {
        Write-Host "❌ Erro ao iniciar serviço: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Parar serviço
function Stop-GenesysService {
    Write-Host "⏹️ PARANDO SERVIÇO GENESYS" -ForegroundColor Yellow
    Write-Host "-" * 40
    
    try {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if (-not $Service) {
            Write-Host "❌ Serviço '$ServiceName' não está instalado!" -ForegroundColor Red
            return $false
        }
        
        if ($Service.Status -eq "Stopped") {
            Write-Host "✅ Serviço já está parado!" -ForegroundColor Green
            return $true
        }
        
        Write-Host "⏹️ Parando serviço..." -ForegroundColor Yellow
        Stop-Service -Name $ServiceName -Force
        
        Write-Host "✅ Serviço parado com sucesso!" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "❌ Erro ao parar serviço: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Reiniciar serviço
function Restart-GenesysService {
    Write-Host "🔄 REINICIANDO SERVIÇO GENESYS" -ForegroundColor Cyan
    Write-Host "-" * 40
    
    $StopResult = Stop-GenesysService
    if ($StopResult) {
        Start-Sleep 2
        return Start-GenesysService
    }
    return $false
}

# Status do serviço
function Get-GenesysServiceStatus {
    Write-Host "📊 STATUS DO SERVIÇO GENESYS" -ForegroundColor Cyan
    Write-Host "-" * 40
    
    try {
        $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if (-not $Service) {
            Write-Host "❌ Serviço '$ServiceName' não está instalado" -ForegroundColor Red
            Write-Host "💡 Use: -Action install para instalar" -ForegroundColor Yellow
            return $false
        }
        
        $StatusColor = switch ($Service.Status) {
            "Running" { "Green" }
            "Stopped" { "Red" }
            default { "Yellow" }
        }
        
        Write-Host "🔹 Nome: $($Service.Name)" -ForegroundColor White
        Write-Host "🔹 Status: $($Service.Status)" -ForegroundColor $StatusColor
        Write-Host "🔹 Tipo de Início: $($Service.StartType)" -ForegroundColor White
        
        # Verificar conectividade se estiver rodando
        if ($Service.Status -eq "Running") {
            Write-Host "🧪 Testando conectividade..." -ForegroundColor Yellow
            try {
                $Response = Invoke-WebRequest -Uri "http://localhost:$Port/" -UseBasicParsing -TimeoutSec 5
                if ($Response.StatusCode -eq 200) {
                    $Data = $Response.Content | ConvertFrom-Json
                    Write-Host "✅ API respondendo: $($Data.message)" -ForegroundColor Green
                } else {
                    Write-Host "⚠️ API não respondendo corretamente" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "⚠️ API não acessível (pode estar carregando)" -ForegroundColor Yellow
            }
        }
        
        # Mostrar logs recentes se existirem
        if (Test-Path $ServiceLog) {
            Write-Host "📋 Logs recentes:" -ForegroundColor Cyan
            Get-Content $ServiceLog -Tail 5 | ForEach-Object {
                Write-Host "   $_" -ForegroundColor Gray
            }
        }
        
        return $true
        
    } catch {
        Write-Host "❌ Erro ao verificar status: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Função principal
function Main {
    # Instalar NSSM se necessário
    if (-not (Install-NSSM)) {
        exit 1
    }
    
    # Verificar pré-requisitos (exceto para remove e status)
    if ($Action -notin @("remove", "status")) {
        if (-not (Test-Prerequisites)) {
            exit 1
        }
    }
    
    # Executar ação
    $Success = switch ($Action) {
        "install" { Install-GenesysService }
        "remove" { Remove-GenesysService }
        "start" { Start-GenesysService }
        "stop" { Stop-GenesysService }
        "restart" { Restart-GenesysService }
        "status" { Get-GenesysServiceStatus }
        default { 
            Write-Host "❌ Ação inválida: $Action" -ForegroundColor Red
            $false
        }
    }
    
    Write-Host ""
    if ($Success) {
        Write-Host "✅ Operação '$Action' concluída com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "❌ Operação '$Action' falhou!" -ForegroundColor Red
        exit 1
    }
    
    # Mostrar comandos úteis
    Write-Host ""
    Write-Host "🎯 COMANDOS ÚTEIS:" -ForegroundColor Magenta
    Write-Host "  Instalar:   .\scripts\setup_genesys_service.ps1 -Action install" -ForegroundColor White
    Write-Host "  Iniciar:    .\scripts\setup_genesys_service.ps1 -Action start" -ForegroundColor White  
    Write-Host "  Status:     .\scripts\setup_genesys_service.ps1 -Action status" -ForegroundColor White
    Write-Host "  Parar:      .\scripts\setup_genesys_service.ps1 -Action stop" -ForegroundColor White
    Write-Host "  Reiniciar:  .\scripts\setup_genesys_service.ps1 -Action restart" -ForegroundColor White
    Write-Host "  Remover:    .\scripts\setup_genesys_service.ps1 -Action remove" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Logs: $ServiceLog" -ForegroundColor Cyan
    Write-Host "🌐 URL: http://localhost:$Port" -ForegroundColor Cyan
}

# Executar
Main
