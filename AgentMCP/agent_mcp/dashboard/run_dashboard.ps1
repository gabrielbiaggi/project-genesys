# Wrapper para iniciar o Dashboard do Agent-MCP com o ambiente correto.

param (
    [string]$NpmPath,
    [string]$LogFile
)

# **CORREÇÃO: Define o diretório de trabalho para o local do script.**
# $PSScriptRoot é uma variável automática no PowerShell que contém o diretório do script atual.
Set-Location -Path $PSScriptRoot

# Validação dos parâmetros
if (-not $NpmPath -or -not (Test-Path $NpmPath)) {
    Write-Error "O caminho para o NPM é inválido ou não foi fornecido."
    exit 1
}
if (-not $LogFile) {
    Write-Error "O caminho para o arquivo de log não foi fornecido."
    exit 1
}

# Adiciona o diretório do Node.js/NPM ao PATH da sessão atual
$npmDir = Split-Path -Path $NpmPath -Parent
$env:PATH = "$npmDir;$env:PATH"

Write-Output "PATH atualizado para incluir: $npmDir"
Write-Output "Iniciando 'npm run dev'..."

# Executa o comando e redireciona toda a saída (stdout e stderr) para o arquivo de log
# O '&' é o operador de chamada no PowerShell para executar comandos.
& $NpmPath run dev *>&1 | Tee-Object -FilePath $LogFile
