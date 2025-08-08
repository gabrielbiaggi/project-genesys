# scripts/start_simple.ps1
# Versão simplificada para iniciar o servidor

param(
    [int]$Port = 8002,
    [string]$LogFile = "genesys_server.log"
)

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$VenvPath = Join-Path $ProjectRoot "venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$LogPath = Join-Path $ProjectRoot $LogFile

Write-Host "🚀 GENESYS STARTER SIMPLES" -ForegroundColor Magenta
Write-Host "=" * 40 -ForegroundColor Gray
Write-Host "📁 Projeto: $ProjectRoot" -ForegroundColor Cyan
Write-Host "🐍 Python: $PythonExe" -ForegroundColor Cyan
Write-Host "🌐 Porta: $Port" -ForegroundColor Cyan
Write-Host "📄 Log: $LogPath" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Gray

# Verifica Python
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Python não encontrado" -ForegroundColor Red
    Write-Host "💡 Execute primeiro: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python encontrado" -ForegroundColor Green

# Verifica se a porta está livre (verificação simples)
try {
    $Connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($Connection) {
        Write-Host "⚠️ Porta $Port pode estar em uso" -ForegroundColor Yellow
        Write-Host "💡 Tentando mesmo assim..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Porta $Port disponível" -ForegroundColor Green
    }
} catch {
    Write-Host "✅ Porta $Port provavelmente disponível" -ForegroundColor Green
}

# Instala dependências básicas se necessárias
Write-Host "📦 Verificando dependências..." -ForegroundColor Cyan
$Missing = @()

@("psutil", "fastapi", "uvicorn") | ForEach-Object {
    try {
        & $PythonExe -c "import $($_)" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $Missing += $_
        }
    } catch {
        $Missing += $_
    }
}

if ($Missing.Count -gt 0) {
    Write-Host "⬇️ Instalando dependências faltantes: $($Missing -join ', ')" -ForegroundColor Yellow
    
    foreach ($Package in $Missing) {
        & $PythonExe -m pip install $Package
    }
} else {
    Write-Host "✅ Dependências básicas OK" -ForegroundColor Green
}

# Comando para iniciar o servidor
$ServerScript = Join-Path $ProjectRoot "scripts\start_genesys_server.py"

if (-not (Test-Path $ServerScript)) {
    Write-Host "❌ Script do servidor não encontrado: $ServerScript" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Iniciando servidor..." -ForegroundColor Cyan
Write-Host "💡 Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Gray

try {
    # Inicia o processo e redireciona saída
    $ProcessParams = @{
        FilePath = $PythonExe
        ArgumentList = $ServerScript, "--port", $Port
        WorkingDirectory = $ProjectRoot
        NoNewWindow = $true
        PassThru = $true
    }
    
    $ServerProcess = Start-Process @ProcessParams
    
    Write-Host "✅ Servidor iniciado com PID: $($ServerProcess.Id)" -ForegroundColor Green
    Write-Host "🌐 URL: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "🌍 Túnel: https://genesys.webcreations.com.br" -ForegroundColor Cyan
    
    # Aguarda o processo
    Wait-Process -Id $ServerProcess.Id
    
} catch {
    Write-Host "❌ Erro ao iniciar: $($_.Exception.Message)" -ForegroundColor Red
    
    # Fallback: executa diretamente
    Write-Host "🔄 Tentando execução direta..." -ForegroundColor Yellow
    
    Set-Location $ProjectRoot
    & $PythonExe $ServerScript --port $Port
}