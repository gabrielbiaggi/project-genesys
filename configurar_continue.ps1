# configurar_continue.ps1
# Script para configurar Continue para funcionar com Genesys local ou remoto

param(
    [string]$Mode = "remoto"  # "local" ou "remoto"
)

Write-Host "🔧 CONFIGURANDO CONTINUE PARA GENESYS" -ForegroundColor Cyan
Write-Host "=" * 50
Write-Host "Modo: $Mode" -ForegroundColor Yellow
Write-Host ""

# Determinar URL base conforme o modo
if ($Mode -eq "local") {
    $apiBase = "http://localhost:8002/v1"
    $description = "Servidor Local"
} else {
    $apiBase = "https://genesys.webcreations.com.br/v1"
    $description = "Servidor Remoto (Cloudflare)"
}

Write-Host "🌐 API Base: $apiBase" -ForegroundColor Green
Write-Host "📋 Descrição: $description" -ForegroundColor White
Write-Host ""

# Configuração do Continue
$continueConfig = @{
    models = @(
        @{
            title = "Genesys $description"
            provider = "openai"
            model = "genesys-local"
            apiBase = $apiBase
            apiKey = "sk-dummy-key-not-needed"
        }
    )
    tabAutocompleteModel = @{
        title = "Genesys $description"
        provider = "openai"
        model = "genesys-local" 
        apiBase = $apiBase
        apiKey = "sk-dummy-key-not-needed"
    }
    customCommands = @(
        @{
            name = "explain"
            prompt = "Explique o seguinte código em português brasileiro: {{{ input }}}"
        },
        @{
            name = "review"
            prompt = "Faça uma revisão detalhada do seguinte código, destacando problemas de performance, segurança e boas práticas: {{{ input }}}"
        },
        @{
            name = "optimize"
            prompt = "Otimize o seguinte código para melhor performance e legibilidade: {{{ input }}}"
        },
        @{
            name = "comment"
            prompt = "Adicione comentários explicativos ao seguinte código: {{{ input }}}"
        }
    )
    allowAnonymousTelemetry = $false
    embeddingsProvider = @{
        provider = "transformers.js"
    }
} | ConvertTo-Json -Depth 10

# Diretório de configuração do Continue
$continueConfigDir = Join-Path $env:USERPROFILE ".continue"
$continueConfigFile = Join-Path $continueConfigDir "config.json"

# Criar diretório se não existir
if (-not (Test-Path $continueConfigDir)) {
    Write-Host "📁 Criando diretório: $continueConfigDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $continueConfigDir -Force | Out-Null
}

# Backup da configuração existente
if (Test-Path $continueConfigFile) {
    $backupFile = "$continueConfigFile.backup.$(Get-Date -Format 'yyyy-MM-dd-HH-mm-ss')"
    Write-Host "💾 Backup da configuração anterior: $backupFile" -ForegroundColor Yellow
    Copy-Item $continueConfigFile $backupFile
}

# Salvar nova configuração
Write-Host "💾 Salvando configuração: $continueConfigFile" -ForegroundColor Green
$continueConfig | Out-File -FilePath $continueConfigFile -Encoding UTF8

Write-Host ""
Write-Host "✅ CONTINUE CONFIGURADO COM SUCESSO!" -ForegroundColor Green
Write-Host "=" * 50
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. 🔄 Reiniciar o Cursor completamente" -ForegroundColor White
Write-Host "2. 📦 Instalar extensão Continue (se ainda não tiver):" -ForegroundColor White
Write-Host "   - Ctrl+Shift+X → Buscar 'Continue'" -ForegroundColor Gray
Write-Host "3. 🧪 Testar:" -ForegroundColor White
Write-Host "   - Abrir um arquivo de código" -ForegroundColor Gray
Write-Host "   - Ctrl+Shift+P → 'Continue: Open'" -ForegroundColor Gray
Write-Host "   - Ou pressionar Ctrl+L para chat" -ForegroundColor Gray
Write-Host ""

# Teste de conectividade
Write-Host "🧪 TESTANDO CONECTIVIDADE..." -ForegroundColor Yellow
$testUrl = if ($Mode -eq "local") { "http://localhost:8002/" } else { "https://genesys.webcreations.com.br/" }

try {
    $response = Invoke-WebRequest -Uri $testUrl -Method GET -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Servidor está respondendo!" -ForegroundColor Green
        
        # Teste específico do endpoint Continue
        $continueTestUrl = "$apiBase/chat/completions"
        Write-Host "🔍 Testando endpoint Continue: $continueTestUrl" -ForegroundColor Yellow
        
        $testPayload = @{
            model = "genesys-local"
            messages = @(
                @{
                    role = "user"
                    content = "teste"
                }
            )
        } | ConvertTo-Json -Depth 10
        
        try {
            $headers = @{
                "Content-Type" = "application/json"
                "Authorization" = "Bearer sk-dummy-key-not-needed"
            }
            
            $continueResponse = Invoke-WebRequest -Uri $continueTestUrl -Method POST -Body $testPayload -Headers $headers -TimeoutSec 10 -UseBasicParsing
            
            if ($continueResponse.StatusCode -eq 200) {
                Write-Host "✅ API Continue funcionando!" -ForegroundColor Green
            } else {
                Write-Host "⚠️ API Continue retornou: $($continueResponse.StatusCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️ Endpoint Continue ainda não disponível (404)" -ForegroundColor Yellow
            Write-Host "💡 Aguarde o servidor ser atualizado com a nova API" -ForegroundColor Cyan
        }
        
    } else {
        Write-Host "⚠️ Servidor retornou: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro de conexão: $($_.Exception.Message)" -ForegroundColor Red
    if ($Mode -eq "local") {
        Write-Host "💡 Inicie o servidor local: .\start_genesys.ps1" -ForegroundColor Cyan
    } else {
        Write-Host "💡 Verifique se o túnel Cloudflare está ativo" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "🎯 COMANDOS ÚTEIS:" -ForegroundColor Magenta
Write-Host "  Continue Chat: Ctrl+L" -ForegroundColor White
Write-Host "  Continue Inline: Ctrl+Shift+L" -ForegroundColor White
Write-Host "  Continue Sidebar: Ctrl+Shift+P → 'Continue: Open'" -ForegroundColor White
Write-Host ""
Write-Host "🔄 MUDAR MODO:" -ForegroundColor Magenta
Write-Host "  Local:  .\configurar_continue.ps1 -Mode local" -ForegroundColor White
Write-Host "  Remoto: .\configurar_continue.ps1 -Mode remoto" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Continue configurado para usar seu Genesys!" -ForegroundColor Green
