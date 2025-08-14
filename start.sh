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

# Verificar que .env existe
if [ -f ".env" ]; then
    echo "✅ .env encontrado"
    echo "📋 Contenido de .env:"
    cat .env
else
    echo "⚠️ .env no encontrado, creando uno básico..."
    cat > .env << EOF
NODE_ENV=production
VITE_BACKEND_URL=/api
FLASK_ENV=production
FLASK_DEBUG=false
EOF
fi

# Obtener el puerto de Railway
PORT=${PORT:-3000}
echo "🌐 Puerto: $PORT"
echo "🔍 Variables de entorno:"
env | grep -E "(PORT|RAILWAY|NODE_ENV)" || echo "No se encontraron variables específicas"

# Verificar que el puerto esté disponible
echo "🔍 Verificando puerto $PORT..."
if command -v netstat &> /dev/null; then
    netstat -tuln | grep ":$PORT " || echo "Puerto $PORT parece estar libre"
fi

# Iniciar la aplicación
echo "🚀 Iniciando aplicación..."
echo "🔍 Health check disponible en: http://localhost:$PORT/health"
echo "🧪 Test disponible en: http://localhost:$PORT/test"
echo "🏠 Home disponible en: http://localhost:$PORT/"

# Ejecutar la aplicación con logging detallado
exec python test_app.py
