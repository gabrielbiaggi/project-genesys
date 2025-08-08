# scripts/setup_cloudflare_tunnel.ps1
# Este script automatiza a instalação do Cloudflare Tunnel como um serviço persistente no Windows usando NSSM.

# --- Parâmetros ---
$CloudflaredURL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$NssmURL = "https://nssm.cc/release/nssm-2.24.zip"
$InstallDir = "C:\ProgramData\GenesysService"
$ServiceName = "GenesysCloudflaredTunnel"
$CloudflareToken = "eyJhIjoiN2YxMmMxY2Y4MjkwM2VhM2IwMzUxN2Y4MzQyOTUxNjkiLCJ0IjoiY2M2MDQ0OTYtZDBhMy00MWIxLWE5YTMtODI5OTI2NjY4YjE0IiwicyI6Ik9UVTJPR1ZtTWpVdE16SmxZaTAwTVdaa0xXSXlNRFF0T0RjNVpHTTFOamt4TkRNNCJ9" # IMPORTANTE: Substitua este valor pelo seu token do Cloudflare.

# --- Verificação de Privilégios ---
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Este script precisa ser executado como Administrador. Por favor, abra um novo PowerShell com 'Executar como Administrador' e tente novamente."
    exit 1
}

# --- Início da Execução ---
Write-Host "Iniciando a configuração do Cloudflare Tunnel..." -ForegroundColor Cyan

# 1. Preparar o ambiente
Write-Host "Criando diretório de instalação em $InstallDir..."
New-Item -Path $InstallDir -ItemType Directory -Force | Out-Null

# 2. Baixar e instalar o Cloudflared
$CloudflaredPath = Join-Path $InstallDir "cloudflared.exe"
if (-not (Test-Path $CloudflaredPath)) {
    Write-Host "Baixando Cloudflared..."
    Invoke-WebRequest -Uri $CloudflaredURL -OutFile $CloudflaredPath
}
else {
    Write-Host "Cloudflared já existe."
}

# 3. Baixar e extrair o NSSM
$NssmExePath = Join-Path $InstallDir "nssm.exe"
if (-not (Test-Path $NssmExePath)) {
    $NssmZipPath = Join-Path $env:TEMP "nssm.zip"
    Write-Host "Baixando NSSM (Non-Sucking Service Manager)..."
    Invoke-WebRequest -Uri $NssmURL -OutFile $NssmZipPath
    
    Write-Host "Extraindo NSSM..."
    Expand-Archive -Path $NssmZipPath -DestinationPath $InstallDir -Force
    
    # Move o executável correto (64-bit) para o diretório principal
    $NssmArchPath = Join-Path $InstallDir "nssm-2.24\win64\nssm.exe"
    if (Test-Path $NssmArchPath) {
        Move-Item -Path $NssmArchPath -Destination $NssmExePath -Force
    }
    else {
        # Fallback para 32-bit se 64-bit não for encontrado
        $NssmArchPath = Join-Path $InstallDir "nssm-2.24\win32\nssm.exe"
        Move-Item -Path $NssmArchPath -Destination $NssmExePath -Force
    }

    # Limpeza
    Remove-Item -Path (Join-Path $InstallDir "nssm-2.24") -Recurse -Force
    Remove-Item -Path $NssmZipPath -Force
}
else {
    Write-Host "NSSM já existe."
}

# 4. Configurar o serviço do Windows com NSSM
# Primeiro, verifica se o serviço já existe e o remove para garantir uma instalação limpa.
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Serviço '$ServiceName' existente encontrado. Removendo para uma nova instalação..." -ForegroundColor Yellow
    # Para o serviço antes de remover e garante que ele foi parado
    & $NssmExePath stop $ServiceName | Out-Null
    Start-Sleep -Seconds 3
    # Remove o serviço
    & $NssmExePath remove $ServiceName confirm
    Start-Sleep -Seconds 2
}

Write-Host "Instalando o serviço '$ServiceName' com NSSM..."
& $NssmExePath install $ServiceName $CloudflaredPath

Write-Host "Configurando parâmetros do serviço..."
$Arguments = "tunnel --no-autoupdate run --token $CloudflareToken"
& $NssmExePath set $ServiceName AppParameters $Arguments
& $NssmExePath set $ServiceName AppDirectory $InstallDir

# Adiciona log de stdout e stderr para depuração
Write-Host "Configurando arquivos de log para depuração..."
$StdOutLog = Join-Path $InstallDir "cloudflared-stdout.log"
$StdErrLog = Join-Path $InstallDir "cloudflared-stderr.log"
& $NssmExePath set $ServiceName AppStdout $StdOutLog
& $NssmExePath set $ServiceName AppStderr $StdErrLog

# Define para iniciar automaticamente
& $NssmExePath set $ServiceName Start SERVICE_AUTO_START

# 5. Iniciar o serviço
Write-Host "Iniciando o serviço '$ServiceName'..."
& $NssmExePath start $ServiceName

Start-Sleep -Seconds 5

# 6. Verificar o status
$status = & $NssmExePath status $ServiceName
Write-Host "Status do Serviço:"
Write-Host "$status"

if ($status -match 'SERVICE_RUNNING') {
    Write-Host "---"
    Write-Host "Configuração do túnel Cloudflare concluída com sucesso!" -ForegroundColor Green
    Write-Host "O serviço '$ServiceName' está rodando em segundo plano e iniciará com o Windows."
}
else {
    Write-Host "---"
    Write-Host "ATENÇÃO: O serviço '$ServiceName' foi instalado, mas não parece estar rodando." -ForegroundColor Yellow
    Write-Host "Verifique os logs de eventos do Windows para mais detalhes."
}
