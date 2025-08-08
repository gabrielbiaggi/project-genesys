# DIAGNOSTICO_CUDA_COMPLETO.ps1 - Diagnóstico TOTAL do CUDA

Write-Host "🔍 DIAGNÓSTICO COMPLETO CUDA WINDOWS" -ForegroundColor Magenta
Write-Host "=" * 60

$CudaEncontrado = $false
$CudaPath = ""
$CudaVersion = ""

# Teste 1: Busca AVANÇADA por instalações CUDA
Write-Host "`n🔍 1. BUSCA AVANÇADA POR CUDA..." -ForegroundColor Yellow
$CudaLocations = @(
    "${env:ProgramFiles}\NVIDIA GPU Computing Toolkit\CUDA",
    "${env:ProgramFiles(x86)}\NVIDIA GPU Computing Toolkit\CUDA", 
    "${env:CUDA_PATH}",
    "${env:CUDA_PATH_V12_6}",
    "${env:CUDA_PATH_V12_5}",
    "${env:CUDA_PATH_V12_4}",
    "${env:CUDA_PATH_V12_3}",
    "${env:CUDA_PATH_V12_2}",
    "${env:CUDA_PATH_V12_1}",
    "${env:CUDA_PATH_V12_0}",
    "${env:CUDA_PATH_V11_8}",
    "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA",
    "C:\CUDA"
)

foreach ($location in $CudaLocations) {
    if ($location -and (Test-Path $location)) {
        Write-Host "✅ CUDA ENCONTRADO: $location" -ForegroundColor Green
        
        # Buscar por versões
        $versions = Get-ChildItem "$location" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "v\d+\.\d+" }
        foreach ($version in $versions) {
            $nvccPath = Join-Path $version.FullName "bin\nvcc.exe"
            if (Test-Path $nvccPath) {
                Write-Host "  ✅ Versão: $($version.Name) - nvcc: $nvccPath" -ForegroundColor Cyan
                $CudaEncontrado = $true
                $CudaPath = $version.FullName
                $CudaVersion = $version.Name
            }
        }
        
        # Se não encontrou versões, verificar diretamente
        $directNvcc = Join-Path $location "bin\nvcc.exe"
        if (Test-Path $directNvcc) {
            Write-Host "  ✅ NVCC direto: $directNvcc" -ForegroundColor Cyan
            $CudaEncontrado = $true
            $CudaPath = $location
        }
    }
}

# Teste 2: Verificar PATH do sistema
Write-Host "`n🔍 2. VERIFICANDO PATH DO SISTEMA..." -ForegroundColor Yellow
$pathEnv = $env:PATH -split ";"
$cudaInPath = $false
foreach ($path in $pathEnv) {
    if ($path -match "CUDA" -or $path -match "nvcc") {
        Write-Host "✅ CUDA no PATH: $path" -ForegroundColor Green
        $cudaInPath = $true
    }
}
if (-not $cudaInPath) {
    Write-Host "⚠️ CUDA não encontrado no PATH" -ForegroundColor Yellow
}

# Teste 3: Teste direto de comandos
Write-Host "`n🔍 3. TESTE DIRETO DE COMANDOS..." -ForegroundColor Yellow

# nvcc test
try {
    $nvccOut = & nvcc --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ nvcc COMANDO FUNCIONA!" -ForegroundColor Green
        $nvccOut | Where-Object { $_ -match "release" } | ForEach-Object { 
            Write-Host "  🎯 $_" -ForegroundColor White 
        }
        $CudaEncontrado = $true
    } else {
        Write-Host "❌ nvcc comando falhou: $nvccOut" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ nvcc não encontrado no PATH" -ForegroundColor Red
}

# nvidia-smi test  
try {
    $smiOut = & nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ nvidia-smi FUNCIONA!" -ForegroundColor Green
        $smiOut | ForEach-Object { Write-Host "  🎮 GPU: $_" -ForegroundColor White }
    } else {
        Write-Host "❌ nvidia-smi falhou: $smiOut" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ nvidia-smi não encontrado" -ForegroundColor Red
}

# Teste 4: Variáveis de ambiente DETALHADAS
Write-Host "`n🔍 4. VARIÁVEIS DE AMBIENTE CUDA..." -ForegroundColor Yellow
$cudaVars = Get-ChildItem env: | Where-Object { $_.Name -match "CUDA" }
if ($cudaVars) {
    foreach ($var in $cudaVars) {
        Write-Host "✅ $($var.Name) = $($var.Value)" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ Nenhuma variável CUDA encontrada" -ForegroundColor Yellow
}

# Teste 5: Registry check (instalações NVIDIA)
Write-Host "`n🔍 5. VERIFICANDO REGISTRY NVIDIA..." -ForegroundColor Yellow
try {
    $nvidiaKeys = Get-ChildItem "HKLM:\SOFTWARE\NVIDIA Corporation" -ErrorAction SilentlyContinue
    if ($nvidiaKeys) {
        Write-Host "✅ Entradas NVIDIA no Registry encontradas" -ForegroundColor Green
        $nvidiaKeys | Where-Object { $_.Name -match "CUDA" } | ForEach-Object {
            Write-Host "  🎯 $($_.Name)" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "⚠️ Erro ao verificar registry" -ForegroundColor Yellow
}

# Teste 6: Drivers NVIDIA
Write-Host "`n🔍 6. VERIFICANDO DRIVERS NVIDIA..." -ForegroundColor Yellow
try {
    $drivers = Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -match "NVIDIA" -and $_.Name -match "GeForce|RTX|GTX" }
    if ($drivers) {
        foreach ($driver in $drivers) {
            Write-Host "✅ GPU: $($driver.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️ Drivers GPU NVIDIA não encontrados" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Erro ao verificar drivers" -ForegroundColor Yellow
}

# RESULTADO E AÇÃO
Write-Host "`n" + "=" * 60
Write-Host "📊 RESULTADO DO DIAGNÓSTICO" -ForegroundColor Magenta
Write-Host "=" * 60

if ($CudaEncontrado) {
    Write-Host "🎉 CUDA DETECTADO!" -ForegroundColor Green
    if ($CudaPath) {
        Write-Host "📁 Path: $CudaPath" -ForegroundColor White
        Write-Host "📋 Versão: $CudaVersion" -ForegroundColor White
    }
    
    Write-Host "`n🔧 CONFIGURANDO AMBIENTE..." -ForegroundColor Yellow
    
    # Configurar variáveis se necessário
    if (-not $env:CUDA_PATH -and $CudaPath) {
        $env:CUDA_PATH = $CudaPath
        Write-Host "✅ CUDA_PATH configurado: $CudaPath" -ForegroundColor Green
    }
    
    # Testar compilação
    Write-Host "`n🧪 TESTE DE COMPILAÇÃO SIMPLES..." -ForegroundColor Cyan
    $testCode = @"
#include <stdio.h>
int main() { printf("CUDA Test OK\n"); return 0; }
"@
    
    $testFile = "cuda_test.c"
    $testCode | Out-File -FilePath $testFile -Encoding ASCII
    
    try {
        $nvccPath = if (Test-Path "$CudaPath\bin\nvcc.exe") { "$CudaPath\bin\nvcc.exe" } else { "nvcc" }
        $compileResult = & $nvccPath $testFile -o cuda_test.exe 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ COMPILAÇÃO TESTE OK!" -ForegroundColor Green
            Remove-Item $testFile -ErrorAction SilentlyContinue
            Remove-Item "cuda_test.exe" -ErrorAction SilentlyContinue
        } else {
            Write-Host "⚠️ Compilação teste falhou: $compileResult" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Erro no teste de compilação: $_" -ForegroundColor Yellow
    }
    
    Write-Host "`n🚀 PRÓXIMO PASSO:" -ForegroundColor Green
    Write-Host "Execute: .\RESOLVER_DEFINITIVO.ps1" -ForegroundColor Cyan
    
} else {
    Write-Host "❌ CUDA NÃO DETECTADO CORRETAMENTE!" -ForegroundColor Red
    Write-Host "`n🔧 POSSÍVEIS SOLUÇÕES:" -ForegroundColor Yellow
    Write-Host "1. Reinstalar CUDA Toolkit" -ForegroundColor White
    Write-Host "2. Verificar se instalação foi completa" -ForegroundColor White
    Write-Host "3. Reiniciar o computador" -ForegroundColor White
    Write-Host "4. Executar como Administrador" -ForegroundColor White
    
    Write-Host "`n📥 REINSTALAR CUDA:" -ForegroundColor Cyan
    Write-Host "https://developer.nvidia.com/cuda-downloads" -ForegroundColor White
}

Write-Host "`n" + "=" * 60