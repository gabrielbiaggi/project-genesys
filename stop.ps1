# Script para parar todos os serviços de background do Genesys de forma robusta.

$ErrorActionPreference = "SilentlyContinue"
$LogDir = Join-Path -Path $PSScriptRoot -ChildPath "logs"
$BackendPidFile = Join-Path -Path $LogDir -ChildPath "backend.pid"
$FrontendPidFile = Join-Path -Path $LogDir -ChildPath "frontend.pid"

function Write-Header($message) {
    Write-Host "`n"
    Write-Host "========================================================================" -ForegroundColor Magenta
    Write-Host "🛑 $message" -ForegroundColor Magenta
    Write-Host "========================================================================" -ForegroundColor Magenta
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

# Função para encontrar e parar uma árvore de processos de forma recursiva
function Stop-ProcessTree {
    param(
        [int]$ParentId
    )
    
    # Encontra todos os processos filhos do PID pai
    $childProcesses = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ParentId }
    
    # Para os processos filhos e seus descendentes primeiro (chamada recursiva)
    foreach ($child in $childProcesses) {
        Stop-ProcessTree -ParentId $child.ProcessId
    }
    
    # Finalmente, para o processo pai (ou o processo atual se não houver filhos)
    try {
        $proc = Get-Process -Id $ParentId -ErrorAction Stop
        Write-Host "  -> Parando processo $($proc.Name) (PID: $ParentId)..."
        Stop-Process -Id $ParentId -Force
        Write-Host "     ...sucesso." -ForegroundColor Green
    } catch {
        # O processo pode já ter sido encerrado como parte da árvore de outro processo
        Write-Host "     ...processo (PID: $ParentId) já não estava em execução." -ForegroundColor Yellow
    }
}

Write-Header "Parando Sistema Genesys"

# --- Etapa 1: Parar processos usando os arquivos PID ---
Write-Host "🔎 Tentando parar processos com base nos arquivos PID..."
$backendPid = Get-Content -Path $BackendPidFile -ErrorAction SilentlyContinue
$frontendPid = Get-Content -Path $FrontendPidFile -ErrorAction SilentlyContinue

if ($frontendPid) {
    Write-Host "Parando serviço: Dashboard Frontend (PID: $frontendPid)..."
    Stop-ProcessTree -ParentId $frontendPid
} else {
    Write-Host "Nenhum PID encontrado para o Dashboard Frontend." -ForegroundColor Yellow
}

if ($backendPid) {
    Write-Host "Parando serviço: Agent-MCP Backend (PID: $backendPid)..."
    Stop-ProcessTree -ParentId $backendPid
} else {
    Write-Host "Nenhum PID encontrado para o Agent-MCP Backend." -ForegroundColor Yellow
}

# --- Etapa 2: Verificação adicional por linha de comando para processos órfãos ---
Write-Host "`n🔍 Verificação adicional por linha de comando para processos órfãos..."

# Backend: python ... agent_mcp.cli
$orphanBackend = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*agent_mcp.cli*" }
if ($orphanBackend) {
    Write-Host "Encontrado(s) processo(s) do backend órfão(s). Parando..."
    $orphanBackend | ForEach-Object { Stop-ProcessTree -ParentId $_.ProcessId }
} else {
    Write-Host "Nenhum processo de backend órfão encontrado."
}

# Frontend: node ... start-dev.js or next dev
$orphanFrontend = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*start-dev.js*" -or $_.CommandLine -like "*next*dev*" }
if ($orphanFrontend) {
    Write-Host "Encontrado(s) processo(s) do frontend órfão(s). Parando..."
    $orphanFrontend | ForEach-Object { Stop-ProcessTree -ParentId $_.ProcessId }
} else {
    Write-Host "Nenhum processo de frontend órfão encontrado."
}

# --- Etapa 3: Limpeza Final ---
Write-Host "`n🧹 Limpando arquivos de log e PID..."
Remove-Item -Path $BackendPidFile, $FrontendPidFile -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path -Path $LogDir -ChildPath "*.log"), (Join-Path -Path $LogDir -ChildPath "*.error.log") -ErrorAction SilentlyContinue
Write-Host "Arquivos de log e PID removidos."

Write-Success "Processo de parada concluído."
