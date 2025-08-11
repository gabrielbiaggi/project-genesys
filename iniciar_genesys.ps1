# iniciar_genesys.ps1
# Comando MASTER para gerenciar Genesys como serviço Windows

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "install", "remove", "monitor")]
    [string]$Action = "start",
    
    [Parameter(Mandatory=$false)]
    [switch]$Service,
    
    [Parameter(Mandatory=$false)]
    [switch]$Monitor,
    
    [Parameter(Mandatory=$false)]
    [switch]$Background,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8002,
    
    [Parameter(Mandatory=$false)]
    [string]$Host = "0.0.0.0"
)

# Configurações
$ServiceName = "GenesysAI"
$ProjectRoot = $PSScriptRoot
$ServiceScript = Join-Path $ProjectRoot "scripts\setup_genesys_service.ps1"
$MonitorScript = Join-Path $ProjectRoot "scripts\monitor_genesys_independente.py"
$OldStartScript = Join-Path $ProjectRoot "start_genesys.ps1"

Write-Host "🚀 GENESYS AI - COMANDO MASTER" -ForegroundColor Cyan
Write-Host "=" * 50
Write-Host "Ação: $Action" -ForegroundColor Yellow
Write-Host ""

# Função para verificar se está rodando como admin
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Função para verificar se serviço existe
function Test-ServiceExists {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    return $service -ne $null
}

# Função para verificar se serviço está rodando
function Test-ServiceRunning {
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    return $service -and $service.Status -eq "Running"
}

# Função para testar API
function Test-API {
    param([string]$Url = "http://localhost:$Port")
    
    try {
        $response = Invoke-WebRequest -Uri "$Url/" -UseBasicParsing -TimeoutSec 5
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Função principal para detectar e iniciar
function Start-GenesysIntelligent {
    Write-Host "🧠 DETECÇÃO INTELIGENTE DO SISTEMA" -ForegroundColor Cyan
    Write-Host "-" * 40
    
    $serviceExists = Test-ServiceExists
    $serviceRunning = Test-ServiceRunning
    $apiResponding = Test-API
    
    Write-Host "🔍 Status atual:" -ForegroundColor Yellow
    Write-Host "  📦 Serviço instalado: $(if($serviceExists){'✅ SIM'}else{'❌ NÃO'})"
    Write-Host "  ▶️ Serviço rodando: $(if($serviceRunning){'✅ SIM'}else{'❌ NÃO'})"
    Write-Host "  🌐 API respondendo: $(if($apiResponding){'✅ SIM'}else{'❌ NÃO'})"
    Write-Host ""
    
    # Decisão inteligente
    if ($apiResponding) {
        Write-Host "✅ GENESYS JÁ ESTÁ ATIVO E RESPONDENDO!" -ForegroundColor Green
        Write-Host "🌐 URL Local: http://localhost:$Port" -ForegroundColor Cyan
        Write-Host "🌍 URL Remoto: https://genesys.webcreations.com.br" -ForegroundColor Cyan
        
        if ($Monitor) {
            Write-Host ""
            Write-Host "📊 Iniciando monitor..." -ForegroundColor Yellow
            Start-Monitor
        }
        return $true
    }
    
    if (-not $serviceExists) {
        Write-Host "🔧 INSTALANDO SERVIÇO..." -ForegroundColor Yellow
        
        if (-not (Test-Administrator)) {
            Write-Host "❌ Precisa de privilégios de administrador para instalar serviço" -ForegroundColor Red
            Write-Host "💡 Execute como administrador ou use modo manual:" -ForegroundColor Yellow
            Write-Host "   .\iniciar_genesys.ps1 -Action manual" -ForegroundColor Cyan
            return $false
        }
        
        $installResult = & $ServiceScript -Action install -Port $Port -Host $Host
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Falha ao instalar serviço" -ForegroundColor Red
            return $false
        }
        
        Write-Host "✅ Serviço instalado!" -ForegroundColor Green
    }
    
    if (-not $serviceRunning) {
        Write-Host "🚀 INICIANDO SERVIÇO..." -ForegroundColor Yellow
        
        $startResult = & $ServiceScript -Action start
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Falha ao iniciar serviço" -ForegroundColor Red
            return $false
        }
        
        # Aguardar inicialização
        Write-Host "⏳ Aguardando inicialização da API..." -ForegroundColor Yellow
        $attempts = 0
        $maxAttempts = 30
        
        do {
            Start-Sleep 2
            $attempts++
            $apiResponding = Test-API
            Write-Host "." -NoNewline -ForegroundColor Yellow
        } while (-not $apiResponding -and $attempts -lt $maxAttempts)
        
        Write-Host ""
        
        if ($apiResponding) {
            Write-Host "✅ GENESYS INICIADO COM SUCESSO!" -ForegroundColor Green
            Write-Host "🌐 URL Local: http://localhost:$Port" -ForegroundColor Cyan
            Write-Host "🌍 URL Remoto: https://genesys.webcreations.com.br" -ForegroundColor Cyan
        } else {
            Write-Host "⚠️ Serviço iniciou mas API ainda não responde" -ForegroundColor Yellow
            Write-Host "💡 Aguarde alguns minutos para carregamento do modelo" -ForegroundColor Cyan
        }
    }
    
    if ($Monitor) {
        Write-Host ""
        Write-Host "📊 Iniciando monitor..." -ForegroundColor Yellow
        Start-Monitor
    }
    
    return $true
}

# Função para iniciar monitor
function Start-Monitor {
    Write-Host "📊 INICIANDO MONITOR INDEPENDENTE" -ForegroundColor Cyan
    Write-Host "-" * 40
    
    if ($Background) {
        Write-Host "🔄 Executando monitor em background..." -ForegroundColor Yellow
        Start-Process -FilePath "python" -ArgumentList "$MonitorScript --background" -NoNewWindow
        Write-Host "✅ Monitor iniciado em background" -ForegroundColor Green
    } else {
        Write-Host "🖥️ Executando monitor interativo..." -ForegroundColor Yellow
        Write-Host "💡 Feche esta janela para parar o monitor" -ForegroundColor Cyan
        Write-Host ""
        & python $MonitorScript
    }
}

# Função para modo manual (compatibilidade)
function Start-GenesysManual {
    Write-Host "🔧 MODO MANUAL (COMPATIBILIDADE)" -ForegroundColor Yellow
    Write-Host "-" * 40
    Write-Host "💡 Executando modo tradicional do terminal..." -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path $OldStartScript) {
        & $OldStartScript
    } else {
        Write-Host "❌ Script manual não encontrado: $OldStartScript" -ForegroundColor Red
        Write-Host "💡 Use o modo serviço: .\iniciar_genesys.ps1" -ForegroundColor Yellow
    }
}

# Função principal de ação
function Invoke-Action {
    switch ($Action.ToLower()) {
        "start" {
            if ($Service -or (Test-ServiceExists)) {
                Start-GenesysIntelligent
            } else {
                Write-Host "🎯 MODO PREFERIDO: SERVIÇO WINDOWS" -ForegroundColor Magenta
                Write-Host "Para usar como serviço (recomendado):" -ForegroundColor White
                Write-Host "  .\iniciar_genesys.ps1 -Service" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "🔧 Executando modo manual..." -ForegroundColor Yellow
                Start-GenesysManual
            }
        }
        
        "stop" {
            if (Test-ServiceExists) {
                Write-Host "⏹️ Parando serviço..." -ForegroundColor Yellow
                & $ServiceScript -Action stop
            } else {
                Write-Host "❌ Serviço não está instalado" -ForegroundColor Red
            }
        }
        
        "restart" {
            if (Test-ServiceExists) {
                Write-Host "🔄 Reiniciando serviço..." -ForegroundColor Yellow
                & $ServiceScript -Action restart
            } else {
                Write-Host "❌ Serviço não está instalado" -ForegroundColor Red
            }
        }
        
        "status" {
            if (Test-ServiceExists) {
                & $ServiceScript -Action status
            } else {
                Write-Host "❌ Serviço não está instalado" -ForegroundColor Red
                Write-Host "💡 Para instalar: .\iniciar_genesys.ps1 -Action install" -ForegroundColor Yellow
            }
        }
        
        "install" {
            if (-not (Test-Administrator)) {
                Write-Host "❌ Precisa de privilégios de administrador" -ForegroundColor Red
                return
            }
            Write-Host "📦 Instalando serviço..." -ForegroundColor Yellow
            & $ServiceScript -Action install -Port $Port -Host $Host
        }
        
        "remove" {
            if (-not (Test-Administrator)) {
                Write-Host "❌ Precisa de privilégios de administrador" -ForegroundColor Red
                return
            }
            Write-Host "🗑️ Removendo serviço..." -ForegroundColor Red
            & $ServiceScript -Action remove
        }
        
        "monitor" {
            Start-Monitor
        }
        
        "manual" {
            Start-GenesysManual
        }
        
        default {
            Write-Host "❌ Ação inválida: $Action" -ForegroundColor Red
        }
    }
}

# Menu de ajuda
function Show-Help {
    Write-Host ""
    Write-Host "🎯 COMANDOS DISPONÍVEIS:" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "🚀 BÁSICOS:" -ForegroundColor Cyan
    Write-Host "  .\iniciar_genesys.ps1                    # Detecta e inicia automaticamente"
    Write-Host "  .\iniciar_genesys.ps1 -Service           # Força modo serviço"
    Write-Host "  .\iniciar_genesys.ps1 -Monitor           # Inicia com monitor"
    Write-Host "  .\iniciar_genesys.ps1 -Action status     # Ver status"
    Write-Host ""
    Write-Host "🔧 GERENCIAMENTO:" -ForegroundColor Cyan
    Write-Host "  .\iniciar_genesys.ps1 -Action install    # Instalar serviço (como admin)"
    Write-Host "  .\iniciar_genesys.ps1 -Action start      # Iniciar serviço"
    Write-Host "  .\iniciar_genesys.ps1 -Action stop       # Parar serviço"
    Write-Host "  .\iniciar_genesys.ps1 -Action restart    # Reiniciar serviço"
    Write-Host "  .\iniciar_genesys.ps1 -Action remove     # Remover serviço (como admin)"
    Write-Host ""
    Write-Host "📊 MONITORAMENTO:" -ForegroundColor Cyan
    Write-Host "  .\iniciar_genesys.ps1 -Action monitor    # Monitor interativo"
    Write-Host "  .\iniciar_genesys.ps1 -Monitor -Background # Monitor em background"
    Write-Host ""
    Write-Host "⚙️ OPÇÕES:" -ForegroundColor Cyan
    Write-Host "  -Port 8002                               # Porta customizada"
    Write-Host "  -Host 0.0.0.0                           # Host customizado"
    Write-Host "  -Force                                   # Forçar operação"
    Write-Host ""
    Write-Host "💡 EXEMPLOS:" -ForegroundColor Yellow
    Write-Host "  .\iniciar_genesys.ps1 -Service -Monitor  # Serviço + Monitor"
    Write-Host "  .\iniciar_genesys.ps1 -Action manual     # Modo terminal tradicional"
    Write-Host ""
}

# Executar ação principal
try {
    if ($args -contains "--help" -or $args -contains "-h") {
        Show-Help
        exit 0
    }
    
    Invoke-Action
    
    if ($Action -eq "start" -and (Test-API)) {
        Write-Host ""
        Write-Host "🎉 GENESYS ESTÁ PRONTO!" -ForegroundColor Green
        Write-Host "=" * 30
        Write-Host "🌐 Local:  http://localhost:$Port" -ForegroundColor Cyan
        Write-Host "🌍 Remoto: https://genesys.webcreations.com.br" -ForegroundColor Cyan
        Write-Host "📚 Docs:   http://localhost:$Port/docs" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🎮 Para monitorar: .\iniciar_genesys.ps1 -Action monitor" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Erro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}