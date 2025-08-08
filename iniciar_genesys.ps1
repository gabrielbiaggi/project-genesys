# iniciar_genesys.ps1
# Script MASTER para iniciar Genesys (substitui scripts redundantes)

param(
    [switch]$Teste,
    [switch]$GPU,
    [switch]$Remoto
)

Write-Host "🚀 GENESYS AI - INICIADOR MASTER" -ForegroundColor Magenta
Write-Host "=" * 40

$ProjectRoot = Get-Location
$PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"

# Verificar Python
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Virtual environment não encontrado" -ForegroundColor Red
    Write-Host "💡 Execute: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Ativar ambiente
Write-Host "🐍 Ativando ambiente virtual..." -ForegroundColor Cyan
& "$ProjectRoot\venv\Scripts\Activate.ps1"

# Verificar .env
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ Arquivo .env não encontrado - criado automaticamente" -ForegroundColor Yellow
}

# Teste GPU se solicitado
if ($GPU) {
    Write-Host "`n🎮 TESTANDO GPU..." -ForegroundColor Cyan
    & $PythonExe "testar_gpu_real.py"
    Write-Host ""
}

# Teste completo se solicitado
if ($Teste) {
    Write-Host "`n🧪 EXECUTANDO TESTES..." -ForegroundColor Cyan
    if ($Remoto) {
        & $PythonExe "testar_genesys_completo.py" --remoto
    } else {
        & $PythonExe "testar_genesys_completo.py" --local
    }
    exit 0
}

# Iniciar servidor principal
Write-Host "🚀 INICIANDO SERVIDOR GENESYS..." -ForegroundColor Green
Write-Host "📡 Local: http://localhost:8002" -ForegroundColor White
Write-Host "🌐 Remoto: https://genesys.webcreations.com.br" -ForegroundColor White
Write-Host "📚 Docs: http://localhost:8002/docs" -ForegroundColor White
Write-Host "⌨️ Pressione Ctrl+C para parar" -ForegroundColor Gray
Write-Host ""

try {
    & $PythonExe "scripts\start_genesys_server.py"
} catch {
    Write-Host "❌ Erro ao iniciar servidor: $_" -ForegroundColor Red
    Write-Host "💡 Tente: .\scripts\start_simple.ps1" -ForegroundColor Yellow
}

Write-Host "`n👋 Servidor Genesys parado" -ForegroundColor Yellow
