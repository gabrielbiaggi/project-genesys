# instalar_extensao_cursor_corrigido.ps1
# Script CORRIGIDO para instalar a extensão Genesys no Cursor

param(
    [switch]$Force
)

Write-Host "🔧 INSTALAÇÃO CORRIGIDA DA EXTENSÃO GENESYS PARA CURSOR" -ForegroundColor Cyan
Write-Host "=" * 60

# Diretórios
$ProjectRoot = Get-Location
$SourceDir = Join-Path $ProjectRoot "cursor-genesys-extension"
$CursorExtensionsDir = Join-Path $env:USERPROFILE ".cursor\extensions"
$TargetDir = Join-Path $CursorExtensionsDir "genesys-ai-assistant"

# Verificar se a pasta source existe
if (-not (Test-Path $SourceDir)) {
    Write-Host "❌ ERRO: Pasta 'cursor-genesys-extension' não encontrada!" -ForegroundColor Red
    Write-Host "📁 Procurando em: $SourceDir" -ForegroundColor Yellow
    exit 1
}

# Criar diretório de extensões se não existir
if (-not (Test-Path $CursorExtensionsDir)) {
    Write-Host "📁 Criando diretório de extensões: $CursorExtensionsDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $CursorExtensionsDir -Force | Out-Null
}

# Remover instalação anterior se existir
if (Test-Path $TargetDir) {
    if ($Force -or (Read-Host "⚠️ Extensão já existe. Remover? (y/N)") -eq 'y') {
        Write-Host "🗑️ Removendo instalação anterior..." -ForegroundColor Yellow
        Remove-Item -Path $TargetDir -Recurse -Force
    } else {
        Write-Host "❌ Instalação cancelada pelo usuário" -ForegroundColor Red
        exit 1
    }
}

# Copiar extensão
Write-Host "📂 Copiando extensão para: $TargetDir" -ForegroundColor Green
try {
    Copy-Item -Path $SourceDir -Destination $TargetDir -Recurse -Force
    Write-Host "✅ Extensão copiada com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRO ao copiar extensão: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Instalar dependências
Write-Host "📦 Instalando dependências npm..." -ForegroundColor Yellow
Push-Location $TargetDir
try {
    $npmOutput = npm install 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependências instaladas!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Aviso durante npm install: $npmOutput" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ ERRO durante npm install: $($_.Exception.Message)" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Compilar TypeScript
Write-Host "🔨 Compilando TypeScript..." -ForegroundColor Yellow
try {
    $compileOutput = npm run compile 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Compilação bem-sucedida!" -ForegroundColor Green
    } else {
        Write-Host "❌ ERRO na compilação: $compileOutput" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} catch {
    Write-Host "❌ ERRO durante compilação: $($_.Exception.Message)" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# Verificar arquivos essenciais
$essentialFiles = @(
    "package.json",
    "out/extension.js",
    "out/genesysApi.js",
    "out/chatProvider.js"
)

Write-Host "🔍 Verificando arquivos essenciais..." -ForegroundColor Yellow
$allFilesExist = $true
foreach ($file in $essentialFiles) {
    $filePath = Join-Path $TargetDir $file
    if (Test-Path $filePath) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - FALTANDO!" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "❌ Alguns arquivos essenciais estão faltando!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. ✅ Extensão instalada em: $TargetDir" -ForegroundColor White
Write-Host "2. 🔄 REINICIE O CURSOR completamente" -ForegroundColor Yellow
Write-Host "3. 🧪 Verificar extensão: Ctrl+Shift+P → 'Extensions: Show Installed Extensions'" -ForegroundColor White
Write-Host "4. 🤖 Procurar por 'Genesys AI Assistant' na lista" -ForegroundColor White
Write-Host "5. 🎮 Testar: Ctrl+Shift+G (chat) ou procurar ícone 🤖 na barra inferior" -ForegroundColor White
Write-Host ""
Write-Host "🔧 SE NÃO APARECER:" -ForegroundColor Yellow
Write-Host "- Ctrl+Shift+P → 'Developer: Reload Window'" -ForegroundColor White
Write-Host "- Verificar se o Cursor está atualizado" -ForegroundColor White
Write-Host "- Reiniciar o Cursor completamente" -ForegroundColor White
Write-Host ""
Write-Host "📡 CONFIGURAÇÃO CONTINUE (Alternativa):" -ForegroundColor Magenta
Write-Host "1. Instalar extensão 'Continue' no Cursor" -ForegroundColor White
Write-Host "2. Configurar modelo customizado:" -ForegroundColor White
Write-Host "   - API Base: https://genesys.webcreations.com.br" -ForegroundColor Cyan
Write-Host "   - Model: genesys-local" -ForegroundColor Cyan
Write-Host "   - Endpoint: /v1/chat/completions" -ForegroundColor Cyan
Write-Host ""

# Oferecer configuração automática do Continue
$setupContinue = Read-Host "🤖 Configurar Continue automaticamente? (y/N)"
if ($setupContinue -eq 'y') {
    Write-Host "🔧 Configurando Continue..." -ForegroundColor Yellow
    
    $continueConfig = @{
        models = @(
            @{
                title = "Genesys Local"
                provider = "openai"
                model = "genesys-local"
                apiBase = "https://genesys.webcreations.com.br"
                apiKey = "sk-dummy-key-not-needed"
            }
        )
        tabAutocompleteModel = @{
            title = "Genesys Local"
            provider = "openai"
            model = "genesys-local"
            apiBase = "https://genesys.webcreations.com.br"
            apiKey = "sk-dummy-key-not-needed"
        }
    } | ConvertTo-Json -Depth 10
    
    $continueConfigDir = Join-Path $env:USERPROFILE ".continue"
    $continueConfigFile = Join-Path $continueConfigDir "config.json"
    
    if (-not (Test-Path $continueConfigDir)) {
        New-Item -ItemType Directory -Path $continueConfigDir -Force | Out-Null
    }
    
    $continueConfig | Out-File -FilePath $continueConfigFile -Encoding UTF8
    Write-Host "✅ Continue configurado! Arquivo: $continueConfigFile" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 TESTE RÁPIDO:" -ForegroundColor Green
Write-Host "curl https://genesys.webcreations.com.br/v1/chat/completions -H 'Content-Type: application/json' -d '{""messages"":[{""role"":""user"",""content"":""teste""}]}'" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Sua IA personalizada está pronta para usar no Cursor!" -ForegroundColor Green
