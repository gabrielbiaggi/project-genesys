# Script para iniciar todos os serviços de background do Genesys (Backend e Frontend).

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

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

function Write-Info($message) {
    Write-Host "ℹ️ $message" -ForegroundColor Gray
}

# --- Início da Execução ---
Write-Header "Iniciando Sistema Genesys"

# Define o caminho do modelo explicitamente como uma variável de ambiente
# Isso garante que o GenesysAgent encontre o modelo sem depender de um arquivo .env
$env:MODEL_PATH = Join-Path -Path $PSScriptRoot -ChildPath "models\llama-3-70b-instruct.Q4_K_M.gguf"
Write-Info "Variável de ambiente MODEL_PATH definida como: $env:MODEL_PATH"

# --- Configurações ---
$ProjectDir = $PSScriptRoot
$LogDir = Join-Path -Path $ProjectDir -ChildPath "logs"
New-Item -ItemType Directory -Path $LogDir -ErrorAction SilentlyContinue

$BackendPidFile = Join-Path -Path $LogDir -ChildPath "backend.pid"
$FrontendPidFile = Join-Path -Path $LogDir -ChildPath "frontend.pid"
$BackendLogFile = Join-Path -Path $LogDir -ChildPath "backend.log"
$BackendErrorFile = Join-Path -Path $LogDir -ChildPath "backend.error.log"
$FrontendLogFile = Join-Path -Path $LogDir -ChildPath "frontend.log"
$FrontendErrorFile = Join-Path -Path $LogDir -ChildPath "frontend.error.log"

# Limpar logs e PIDs antigos
Write-Info "Limpando logs e arquivos PID antigos..."
Remove-Item -Path $BackendLogFile, $BackendErrorFile, $FrontendLogFile, $FrontendErrorFile, $BackendPidFile, $FrontendPidFile -ErrorAction SilentlyContinue

# --- Iniciar Backend ---
Write-Header "Iniciando Agent-MCP Backend"
$VenvPath = Join-Path -Path $ProjectDir -ChildPath ".venv"
$PythonExe = Join-Path -Path $VenvPath -ChildPath "Scripts\python.exe"
$BackendModulePath = "agent_mcp.cli"
$BackendWorkDir = Join-Path -Path $ProjectDir -ChildPath "AgentMCP"
$WorkspaceDir = Join-Path -Path $ProjectDir -ChildPath "workspace"
New-Item -ItemType Directory -Path $WorkspaceDir -ErrorAction SilentlyContinue

# Define a variável de ambiente MCP_PROJECT_DIR antes de iniciar o processo
# Isso é crítico para que os módulos de configuração a encontrem na importação
$env:MCP_PROJECT_DIR = $WorkspaceDir
Write-Info "Variável de ambiente MCP_PROJECT_DIR definida como: $env:MCP_PROJECT_DIR"

# Usando -WorkingDirectory para uma execução mais robusta
# Removendo aspas simples do caminho - PowerShell as trata literalmente em Start-Process
$BackendArguments = "-m $BackendModulePath --project-dir `"$WorkspaceDir`" --port 8080"
Write-Info "Executando: $PythonExe $BackendArguments"
Write-Info "Diretório de Trabalho: $BackendWorkDir"

# Unifica os logs de saída e erro para simplificar.
New-Item -Path $BackendLogFile -ItemType File -Force | Out-Null
Remove-Item -Path $BackendErrorFile -ErrorAction SilentlyContinue

# Monta o comando completo a ser executado
$Command = "& '$PythonExe' -m $BackendModulePath --project-dir '$WorkspaceDir' --port 8080"
Write-Info "Comando de Execução: $Command"

# Inicia o processo em uma nova janela oculta do PowerShell para isolamento e captura de logs unificados
# O redirecionamento *> captura stdout, stderr e todos os outros fluxos para um único arquivo
$Process = Start-Process pwsh.exe -ArgumentList "-NoProfile -Command `"$Command *>`'$BackendLogFile'`"" -WorkingDirectory $BackendWorkDir -PassThru -WindowStyle Hidden

if ($Process) {
    Start-Sleep -Seconds 3 # Dá tempo para o processo iniciar ou falhar
    if ((Get-Process -Id $Process.Id -ErrorAction SilentlyContinue)) {
        $Process.Id | Out-File -FilePath $BackendPidFile
        Write-Success "Processo do Backend iniciado com PID $($Process.Id). Logs em: $BackendLogFile"
    } else {
        Write-Error "O processo do Backend falhou ao iniciar. Verifique os logs para detalhes."
        if (Test-Path $BackendLogFile) {
            Get-Content $BackendLogFile | Write-Host
        }
        exit 1
    }
} else {
    Write-Error "Falha ao criar o processo do Backend."
    exit 1
}

# --- Iniciar Frontend ---
Write-Header "Iniciando Dashboard Frontend"
$DashboardDir = Join-Path -Path $ProjectDir -ChildPath "AgentMCP\agent_mcp\dashboard"

# Pré-cria os arquivos de log
New-Item -Path $FrontendLogFile -ItemType File -Force | Out-Null
New-Item -Path $FrontendErrorFile -ItemType File -Force | Out-Null

# Inicia 'npm' diretamente usando seu -WorkingDirectory
$frontendProcess = Start-Process "npm.cmd" -ArgumentList "run dev" -WorkingDirectory $DashboardDir -WindowStyle Hidden -PassThru -RedirectStandardOutput $FrontendLogFile -RedirectStandardError $FrontendErrorFile

if ($frontendProcess) {
    # Aguarda um momento para o processo iniciar
    Start-Sleep -Seconds 2
    
    # Verifica se o processo ainda está rodando
    if (!$frontendProcess.HasExited) {
        $frontendProcess.Id | Out-File -FilePath $FrontendPidFile
        Write-Success "Processo do Frontend iniciado com PID $($frontendProcess.Id). Logs em: $FrontendLogFile"
    } else {
        Write-Error "O processo do Frontend falhou ao iniciar. Verifique os logs para detalhes."
        if (Test-Path $FrontendErrorFile) {
            Write-Host "Erros do Frontend:" -ForegroundColor Red
            Get-Content $FrontendErrorFile | Write-Host
        }
        if (Test-Path $FrontendLogFile) {
            Write-Host "Saída do Frontend:" -ForegroundColor Yellow
            Get-Content $FrontendLogFile | Write-Host
        }
        exit 1
    }
} else {
    Write-Error "Falha ao criar o processo do Frontend."
    exit 1
}

Write-Header "Sistema Genesys Iniciado com Sucesso"
Write-Info "Backend (API) rodando na porta 8080."
Write-Info "Frontend (Dashboard) deve estar disponível em http://localhost:3847 em breve."
