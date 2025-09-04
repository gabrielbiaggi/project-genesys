# Verifica se o script está sendo executado como Administrador
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Este script precisa ser executado com privilégios de Administrador para garantir que todas as permissões sejam aplicadas corretamente."
    Write-Warning "Por favor, clique com o botão direito no script e selecione 'Executar como Administrador'."
    # Descomente a linha abaixo para forçar a parada se não for admin.
    # exit 1
}

# --- Configurações ---
$PythonVersionRequired = "3.9"
$VenvDir = ".venv"
$ErrorActionPreference = "Stop"

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
Write-Header "Iniciando a Configuração do Ambiente Genesys"

# 1. Verificar Python
Write-Host "Passo 1: Verificando a versão do Python..."
try {
    $pythonVersion = (python --version 2>&1).Split(' ')[1]
    if ([version]$pythonVersion -lt [version]$PythonVersionRequired) {
        Write-Error-Message "Versão do Python instalada ($pythonVersion) é menor que a requerida ($PythonVersionRequired)."
        exit 1
    }
    Write-Success "Python $pythonVersion encontrado."
}
catch {
    Write-Error-Message "Python não encontrado no PATH. Por favor, instale Python $PythonVersionRequired ou superior e adicione-o ao PATH."
    exit 1
}

# 2. Criar ou recriar Ambiente Virtual
Write-Header "Passo 2: Configurando o Ambiente Virtual Python em '$VenvDir'"
if (Test-Path $VenvDir) {
    Write-Warning "Ambiente virtual existente encontrado. Removendo para garantir uma instalação limpa..."
    Remove-Item $VenvDir -Recurse -Force
}
python -m venv $VenvDir
Write-Success "Ambiente virtual criado com sucesso."

# 3. Ativar e Instalar Dependências Python
Write-Header "Passo 3: Instalando dependências Python"
$ActivateScript = Join-Path -Path $VenvDir -ChildPath "Scripts\Activate.ps1"

# Instalar dependências do Agent-MCP
Write-Host "Instalando dependências do Agent-MCP..."
try {
    & $ActivateScript
    pip install -r ./AgentMCP/requirements.txt
    pip install -r ./AgentMCP/genesys_integration/requirements_genesys.txt
    Write-Success "Dependências Python instaladas com sucesso."
}
catch {
    Write-Error-Message "Falha ao instalar as dependências Python. Verifique os logs de erro."
    exit 1
}

# 4. Instalar Dependências do Dashboard (npm)
Write-Header "Passo 4: Instalando dependências do Dashboard (npm)"
$DashboardDir = ".\AgentMCP\agent_mcp\dashboard"
if (-not (Test-Path $DashboardDir)) {
    Write-Error-Message "Diretório do dashboard não encontrado em '$DashboardDir'."
    exit 1
}

try {
    Push-Location $DashboardDir
    Write-Host "Executando 'npm install' no diretório do dashboard..."
    npm install
    Pop-Location
    Write-Success "Dependências do dashboard instaladas com sucesso."
}
catch {
    Write-Error-Message "Falha ao instalar as dependências do dashboard. Verifique se o Node.js e o npm estão instalados e no PATH."
    Pop-Location
    exit 1
}

Write-Header "🎉 Configuração do Ambiente Concluída com Sucesso!"
Write-Host "Para ativar o ambiente virtual manualmente, execute:" -ForegroundColor Yellow
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
