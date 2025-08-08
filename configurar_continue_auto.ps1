# configurar_continue_auto.ps1
# Configuração automática do Continue baseada no status do servidor

Write-Host "🔧 CONFIGURADOR AUTOMÁTICO CONTINUE" -ForegroundColor Cyan
Write-Host "=" * 40

# Testar servidores
$localOk = $false
$remoteOk = $false

Write-Host "🧪 Testando servidor local..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/" -Method GET -TimeoutSec 3 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        $localOk = $true
        Write-Host "✅ Local funcionando" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Local não disponível" -ForegroundColor Red
}

Write-Host "🧪 Testando servidor remoto..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://genesys.webcreations.com.br/" -Method GET -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        $remoteOk = $true
        Write-Host "✅ Remoto funcionando" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Remoto não disponível" -ForegroundColor Red
}

# Escolher configuração
$mode = "remoto"
if ($localOk -and (-not $remoteOk)) {
    $mode = "local"
    Write-Host "🎯 Configurando para LOCAL (remoto indisponível)" -ForegroundColor Yellow
} elseif ($localOk -and $remoteOk) {
    $mode = "local"
    Write-Host "🎯 Configurando para LOCAL (preferência)" -ForegroundColor Green
} elseif ($remoteOk) {
    $mode = "remoto"
    Write-Host "🎯 Configurando para REMOTO" -ForegroundColor Blue
} else {
    Write-Host "❌ Nenhum servidor disponível!" -ForegroundColor Red
    Write-Host "💡 Inicie o servidor: .\iniciar_genesys.ps1" -ForegroundColor Yellow
    exit 1
}

# Executar configuração
Write-Host "`n🔧 Aplicando configuração..." -ForegroundColor Cyan
& ".\configurar_continue.ps1" -Mode $mode

Write-Host "`n✅ CONTINUE CONFIGURADO!" -ForegroundColor Green
Write-Host "🎯 Modo: $mode" -ForegroundColor White
Write-Host "💡 Reinicie o Cursor para aplicar" -ForegroundColor Yellow
