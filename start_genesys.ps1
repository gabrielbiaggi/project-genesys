# Script PowerShell completo para iniciar o servidor Genesys
# Execute este arquivo e a IA estará no ar!

param(
    [int]$Port = 8002,
    [string]$Host = "0.0.0.0",
    [switch]$CheckOnly,
    [switch]$NoDownload
)

# Configurações
$ErrorActionPreference = "Stop"
$ProjectRoot = Get-Location

Write-Host "🤖 Genesys Server Starter" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Função para exibir mensagens coloridas
function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    
    switch ($Type) {
        "Success" { Write-Host "✅ $Message" -ForegroundColor Green }
        "Error"   { Write-Host "❌ $Message" -ForegroundColor Red }
        "Warning" { Write-Host "⚠️  $Message" -ForegroundColor Yellow }
        "Info"    { Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
        default   { Write-Host "📋 $Message" -ForegroundColor White }
    }
}

# Verifica se o ambiente virtual existe
$VenvPath = Join-Path $ProjectRoot "venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

if (-not (Test-Path $VenvPath)) {
    Write-Status "Ambiente virtual não encontrado. Criando..." "Warning"
    
    try {
        python -m venv venv
        Write-Status "Ambiente virtual criado" "Success"
    }
    catch {
        Write-Status "Erro ao criar ambiente virtual: $_" "Error"
        exit 1
    }
}

if (-not (Test-Path $PythonExe)) {
    Write-Status "Python não encontrado no ambiente virtual" "Error"
    Write-Status "Tente recriar o ambiente: Remove-Item venv -Recurse -Force; python -m venv venv" "Info"
    exit 1
}

Write-Status "Ambiente virtual encontrado" "Success"

# Ativa o ambiente virtual (PowerShell)
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    Write-Status "Ativando ambiente virtual..." "Info"
    & $ActivateScript
} else {
    Write-Status "Script de ativação não encontrado, usando Python direto" "Warning"
}

# Verifica/instala dependências essenciais
$RequiredPackages = @("fastapi", "uvicorn", "python-dotenv", "langchain", "llama-cpp-python")

Write-Status "Verificando dependências..." "Info"

foreach ($Package in $RequiredPackages) {
    try {
        $Result = & $PythonExe -c "import $($Package.Replace('-', '_')); print('OK')" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "$Package - OK" "Success"
        } else {
            throw "Não encontrado"
        }
    }
    catch {
        Write-Status "$Package não encontrado. Instalando..." "Warning"
        
        try {
            & $PythonExe -m pip install $Package
            Write-Status "$Package instalado" "Success"
        }
        catch {
            Write-Status "Erro ao instalar $Package : $_" "Error"
            Write-Status "Tente instalar manualmente: pip install $Package" "Info"
        }
    }
}

# Verifica se existem modelos
$ModelsDir = Join-Path $ProjectRoot "models"
if (-not (Test-Path $ModelsDir)) {
    New-Item -ItemType Directory -Path $ModelsDir -Force | Out-Null
    Write-Status "Diretório de modelos criado" "Info"
}

$GgufFiles = Get-ChildItem -Path $ModelsDir -Filter "*.gguf" -ErrorAction SilentlyContinue
if ($GgufFiles.Count -eq 0) {
    Write-Status "Nenhum modelo encontrado" "Warning"
    
    if (-not $NoDownload) {
        Write-Status "Tentando baixar modelo..." "Info"
        
        $DownloadScript = Join-Path $ProjectRoot "scripts\download_model.py"
        if (Test-Path $DownloadScript) {
            try {
                & $PythonExe $DownloadScript
                Write-Status "Download do modelo concluído" "Success"
            }
            catch {
                Write-Status "Erro no download: $_" "Error"
                Write-Status "Execute manualmente: python scripts\download_model.py" "Info"
            }
        } else {
            Write-Status "Script de download não encontrado" "Warning"
        }
    }
} else {
    foreach ($Model in $GgufFiles) {
        $SizeGB = [math]::Round($Model.Length / 1GB, 1)
        Write-Status "Modelo encontrado: $($Model.Name) ($SizeGB GB)" "Success"
    }
}

# Se é apenas verificação, para aqui
if ($CheckOnly) {
    Write-Status "Verificação concluída" "Success"
    exit 0
}

# Verifica se a porta está disponível
$PortInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($PortInUse) {
    Write-Status "Porta $Port já está em uso" "Error"
    Write-Status "Processos usando a porta:" "Info"
    Get-Process -Id $PortInUse.OwningProcess | Format-Table Name, Id, CPU -AutoSize
    
    $Response = Read-Host "Deseja tentar parar o processo? (s/N)"
    if ($Response -eq 's' -or $Response -eq 'S') {
        try {
            Stop-Process -Id $PortInUse.OwningProcess -Force
            Write-Status "Processo parado" "Success"
            Start-Sleep 2
        }
        catch {
            Write-Status "Erro ao parar processo: $_" "Error"
            exit 1
        }
    } else {
        Write-Status "Use uma porta diferente: .\start_genesis.ps1 -Port 8003" "Info"
        exit 1
    }
}

Write-Status "Porta $Port disponível" "Success"

# Inicia o servidor
Write-Status "Iniciando servidor Genesys..." "Info"
Write-Status "Host: $Host" "Info"
Write-Status "Porta: $Port" "Info"
Write-Status "URL Local: http://localhost:$Port" "Info"
Write-Status "URL Túnel: https://genesys.webcreations.com.br" "Success"

try {
    # Usa o script Python para iniciar
    & $PythonExe "scripts\start_genesys_server.py" --host $Host --port $Port
}
catch {
    Write-Status "Erro ao iniciar servidor: $_" "Error"
    
    # Fallback: inicia diretamente com uvicorn
    Write-Status "Tentando iniciar diretamente com uvicorn..." "Warning"
    try {
        & $PythonExe -m uvicorn app.main:app --host $Host --port $Port --reload
    }
    catch {
        Write-Status "Falha total ao iniciar servidor: $_" "Error"
        exit 1
    }
}

Write-Status "Servidor parado" "Info"
