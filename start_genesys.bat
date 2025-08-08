@echo off
REM Script completo para iniciar o servidor Genesys
REM Execute este arquivo e a IA estará no ar!

echo 🤖 Iniciando Genesys Server...
echo =====================================

REM Ativa o ambiente virtual
echo 📦 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verifica se ativou corretamente
if errorlevel 1 (
    echo ❌ Erro ao ativar o ambiente virtual
    echo 💡 Execute primeiro: python -m venv venv
    pause
    exit /b 1
)

echo ✅ Ambiente virtual ativado

REM Inicia o servidor usando o script Python
echo 🚀 Iniciando servidor...
python scripts\start_genesys_server.py

REM Se chegou aqui, houve erro ou parada
echo.
echo 🛑 Servidor parado
pause
