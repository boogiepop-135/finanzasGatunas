@echo off
echo 🚀 Iniciando aplicación en Railway...
echo 📅 Timestamp: %date% %time%
echo 🔧 Directorio actual: %cd%

REM Verificar que Python esté disponible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    exit /b 1
)
echo ✅ Python encontrado

REM Verificar que Flask esté instalado
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flask no está instalado
    exit /b 1
)
echo ✅ Flask está instalado

REM Verificar que test_app.py existe
if not exist "test_app.py" (
    echo ❌ test_app.py no encontrado
    dir *.py
    exit /b 1
)
echo ✅ test_app.py encontrado

REM Obtener el puerto de Railway
set PORT=%PORT%
if "%PORT%"=="" set PORT=3000
echo 🌐 Puerto: %PORT%

REM Iniciar la aplicación
echo 🚀 Iniciando aplicación...
echo 🔍 Health check disponible en: http://localhost:%PORT%/health
python test_app.py
