# scripts/setup_windows.ps1
# Orquestrador de instalação para o ambiente do Projeto Gênesis no Windows.
# Este script automatiza a criação do ambiente virtual e a instalação de dependências.

# --- Verificação de Privilégios de Administrador ---
$ErrorActionPreference = 'Stop'
$currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Este script requer privilégios de administrador para garantir a correta instalação das dependências." -ForegroundColor Yellow
    Write-Host "Tentando re-executar como Administrador..." -ForegroundColor Yellow
    Start-Process pwsh -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`""
    exit
}

Write-Host "Privilégios de administrador confirmados. Iniciando a configuração..." -ForegroundColor Green

# --- Aviso de Pré-requisitos ---
Write-Host "AVISO IMPORTANTE:" -ForegroundColor Yellow
Write-Host "Este script assume que as 'Ferramentas de Build do C++' do Visual Studio estão instaladas." -ForegroundColor Yellow
Write-Host "Se a instalação falhar no passo do 'llama-cpp-python', por favor, instale-as conforme o README.md." -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------"

# --- Configuração do Ambiente Virtual ---
$venvPath = Join-Path $PSScriptRoot "..\venv"

if (-not (Test-Path -Path $venvPath)) {
    Write-Host "Criando ambiente virtual Python em '$venvPath'..." -ForegroundColor Cyan
    try {
        python -m venv $venvPath
        Write-Host "Ambiente virtual criado com sucesso." -ForegroundColor Green
    } catch {
        Write-Host "ERRO: Falha ao criar o ambiente virtual." -ForegroundColor Red
        Write-Host "Verifique se o Python está instalado e disponível no seu PATH." -ForegroundColor Red
        Write-Host $_.Exception.Message
        exit 1
    }
} else {
    Write-Host "Ambiente virtual já existente em '$venvPath'." -ForegroundColor White
}

# --- Instalação de Dependências ---
$requirementsPath = Join-Path $PSScriptRoot "..\requirements.txt"
Write-Host "Iniciando a instalação de dependências do '$requirementsPath'..." -ForegroundColor Cyan
Write-Host "Este processo pode levar vários minutos, especialmente na compilação do llama-cpp-python..." -ForegroundColor Cyan

$pipPath = Join-Path $venvPath "Scripts\pip.exe"

try {
    & $pipPath install -r $requirementsPath --quiet
    Write-Host "Dependências instaladas com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Falha ao instalar as dependências via pip." -ForegroundColor Red
    Write-Host "Verifique o log de erros acima. A causa mais provável é a falta das Ferramentas de Build do C++." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

Write-Host "---------------------------------------------------------------"
Write-Host "Configuração do Projeto Gênesis concluída com sucesso!" -ForegroundColor Green
Write-Host "O próximo passo é baixar os modelos de IA executando o script 'download_model.py'." -ForegroundColor White
Read-Host -Prompt "Pressione Enter para sair"
