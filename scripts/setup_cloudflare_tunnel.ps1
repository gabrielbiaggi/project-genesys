# scripts/setup_cloudflare_tunnel.ps1

# Parâmetros de Configuração
$CloudflaredURL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$NssmURL = "https://nssm.cc/release/nssm-2.24.zip"
$InstallDir = "C:\ProgramData\Cloudflare" # Diretório de instalação para as ferramentas
$ServiceName = "CloudflaredTunnel"

# Substitua com o token do seu túnel obtido no painel do Cloudflare
$TunnelToken = "COLE_SEU_TOKEN_AQUI"

# --- Início da Execução ---

# 1. Preparar o ambiente
Write-Host "Criando diretório de instalação em $InstallDir..."
New-Item -Path $InstallDir -ItemType Directory -Force | Out-Null

# 2. Baixar e instalar o Cloudflared
$CloudflaredPath = Join-Path $InstallDir "cloudflared.exe"
Write-Host "Baixando Cloudflared..."
Invoke-WebRequest -Uri $CloudflaredURL -OutFile $CloudflaredPath

# 3. Baixar e extrair o NSSM
$NssmZipPath = Join-Path $env:TEMP "nssm.zip"
$NssmExePath = Join-Path $InstallDir "nssm.exe"
Write-Host "Baixando NSSM..."
Invoke-WebRequest -Uri $NssmURL -OutFile $NssmZipPath
Write-Host "Extraindo NSSM..."
Expand-Archive -Path $NssmZipPath -DestinationPath $InstallDir -Force
# Encontra a arquitetura correta (32 ou 64 bits) e move o nssm.exe
$NssmArchPath = Join-Path $InstallDir "nssm-2.24\win64\nssm.exe"
if (-not (Test-Path $NssmArchPath)) {
    $NssmArchPath = Join-Path $InstallDir "nssm-2.24\win32\nssm.exe"
}
Move-Item -Path $NssmArchPath -Destination $NssmExePath -Force
Remove-Item -Path (Join-Path $InstallDir "nssm-2.24") -Recurse -Force
Remove-Item -Path $NssmZipPath -Force

# 4. Configurar o serviço do Windows com NSSM
Write-Host "Configurando o serviço '$ServiceName' com NSSM..."
& $NssmExePath install $ServiceName $CloudflaredPath
& $NssmExePath set $ServiceName AppParameters "tunnel --no-autoupdate run --token $TunnelToken"
& $NssmExePath set $ServiceName AppDirectory $InstallDir
& $NssmExePath set $ServiceName AppStopMethodSkip 6

# 5. Iniciar o serviço
Write-Host "Iniciando o serviço '$ServiceName'..."
& $NssmExePath start $ServiceName

Write-Host "---"
Write-Host "Configuração do túnel Cloudflare concluída com sucesso!"
Write-Host "O serviço '$ServiceName' está rodando em segundo plano."
Write-Host "AVISO: Lembre-se de substituir 'COLE_SEU_TOKEN_AQUI' no script pelo seu token real."
