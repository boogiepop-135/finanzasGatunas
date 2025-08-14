#!/bin/bash

echo "🚀 Iniciando aplicación en Railway..."
echo "📅 Timestamp: $(date)"
echo "🔧 Directorio actual: $(pwd)"
echo "📁 Contenido del directorio:"
ls -la

# Verificar que Python esté disponible
if command -v python &> /dev/null; then
    echo "✅ Python encontrado: $(python --version)"
else
    echo "❌ Python no encontrado"
    exit 1
fi

# Verificar que Flask esté instalado
python -c "import flask" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Flask está instalado"
else
    echo "❌ Flask no está instalado"
    exit 1
fi

# Verificar que test_app.py existe
if [ -f "test_app.py" ]; then
    echo "✅ test_app.py encontrado"
else
    echo "❌ test_app.py no encontrado"
    ls -la *.py
    exit 1
fi

# Obtener el puerto de Railway
PORT=${PORT:-3000}
echo "🌐 Puerto: $PORT"
echo "🔍 Variables de entorno:"
env | grep -E "(PORT|RAILWAY|NODE_ENV)" || echo "No se encontraron variables específicas"

# Iniciar la aplicación
echo "🚀 Iniciando aplicación..."
echo "🔍 Health check disponible en: http://localhost:$PORT/health"
exec python test_app.py
