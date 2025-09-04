# --- Configurações ---
$VenvDir = ".venv"
$ErrorActionPreference = "Stop"
$LogDir = "logs"
$BackendPidFile = Join-Path -Path $PSScriptRoot -ChildPath "$LogDir\backend.pid"
$FrontendPidFile = Join-Path -Path $PSScriptRoot -ChildPath "$LogDir\frontend.pid"

# --- Funções Auxiliares ---
function Write-Header($message) {
    Write-Host "`n"
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "🚀 $message" -ForegroundColor Cyan
    Write-Host "========================================================================" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Error-Message($message) {
    Write-Host "❌ ERRO: $message" -ForegroundColor Red
}

# --- Início da Execução ---
Write-Header "Iniciando Sistema Genesys Completo como Serviço de Background"

# 0. Criar diretório de logs se não existir
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir
}

# 1. Validar Ambiente
$ActivateScript = Join-Path -Path $PSScriptRoot -ChildPath "$VenvDir\Scripts\Activate.ps1"
if (-not (Test-Path $ActivateScript)) {
    Write-Error-Message "Ambiente virtual não encontrado em '$VenvDir'. Execute '.\setup_environment.ps1' primeiro."
    exit 1
}

# 2. Iniciar Agent-MCP Backend
Write-Host "Iniciando o serviço: Agent-MCP Backend..."
try {
    # O comando ativa o venv e depois chama o CLI do agent_mcp, que por sua vez inicia o uvicorn.
    # Isto garante que todas as variáveis de ambiente e lógicas de inicialização sejam executadas.
    $mcpCommand = "& `'$ActivateScript`'; python -m agent_mcp.cli --project-dir `'$PSScriptRoot`'"
    $process = Start-Process pwsh -ArgumentList "-NoProfile", "-Command", $mcpCommand -WindowStyle Hidden -PassThru
    $process.Id | Out-File -FilePath $BackendPidFile
    Write-Success ("Agent-MCP Backend iniciado com sucesso. PID: " + $process.Id)
} catch {
    Write-Error-Message "Falha ao iniciar o serviço Agent-MCP Backend."
    Write-Error-Message $_.Exception.Message
    exit 1
}

# 3. Iniciar Dashboard Frontend
Write-Host "Iniciando o serviço: Dashboard Frontend..."
$dashboardDir = Join-Path -Path $PSScriptRoot -ChildPath "AgentMCP\agent_mcp\dashboard"
try {
    # Executar 'npm run dev' dentro do diretório correto.
    $dashboardCommand = "cd '$dashboardDir'; npm run dev"
    $process = Start-Process pwsh -ArgumentList "-NoProfile", "-Command", $dashboardCommand -WindowStyle Hidden -PassThru
    $process.Id | Out-File -FilePath $FrontendPidFile
    Write-Success ("Dashboard Frontend iniciado com sucesso. PID: " + $process.Id)
} catch {
    Write-Error-Message "Falha ao iniciar o serviço Dashboard Frontend. Verifique se o Node.js está no PATH."
    Write-Error-Message $_.Exception.Message
    # Tenta parar o backend se o frontend falhar
    & ".\stop.ps1"
    exit 1
}

# 4. Mensagem Final
Write-Header "Serviços Iniciados em Background"
Write-Host "Aguarde alguns instantes para a inicialização completa."
Write-Host "URLs de Acesso:" -ForegroundColor Yellow
Write-Host "  - Dashboard: http://localhost:3847" -ForegroundColor Yellow
Write-Host "  - Agent-MCP API: http://localhost:8080" -ForegroundColor Yellow
Write-Host "  - Genesys Agent (após iniciar no dashboard): http://localhost:8002" -ForegroundColor Yellow
Write-Host "`nPara parar os serviços, execute '.\stop.ps1'" -ForegroundColor Gray
