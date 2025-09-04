# --- Configurações ---
$LogDir = "logs"
$BackendPidFile = Join-Path -Path $PSScriptRoot -ChildPath "$LogDir\backend.pid"
$FrontendPidFile = Join-Path -Path $PSScriptRoot -ChildPath "$LogDir\frontend.pid"
$ErrorActionPreference = "SilentlyContinue"

# --- Funções Auxiliares ---
function Write-Header($message) {
    Write-Host "`n"
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "🛑 $message" -ForegroundColor Cyan
    Write-Host "========================================================================" -ForegroundColor Cyan
}

function Stop-ServiceByPidFile {
    param(
        [string]$Name,
        [string]$PidFile
    )

    Write-Host "Parando o serviço: $Name..."
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        
        if ($process) {
            try {
                Stop-Process -Id $pid -Force
                Write-Host "✅ Processo $Name (PID: $pid) finalizado com sucesso." -ForegroundColor Green
            } catch {
                Write-Host "⚠️  Não foi possível parar o processo $Name (PID: $pid). Pode já ter sido finalizado." -ForegroundColor Yellow
            }
        } else {
            Write-Host "ℹ️  Processo $Name (PID: $pid) não encontrado." -ForegroundColor Gray
        }
        Remove-Item $PidFile -Force
    } else {
        Write-Host "ℹ️  Arquivo PID para $Name não encontrado. O serviço pode não estar rodando." -ForegroundColor Gray
    }
}

# --- Início da Execução ---
Write-Header "Parando Sistema Genesys"

Stop-ServiceByPidFile -Name "Dashboard Frontend" -PidFile $FrontendPidFile
Stop-ServiceByPidFile -Name "Agent-MCP Backend" -PidFile $BackendPidFile

Write-Header "Processos de Background Finalizados"
