#!/bin/bash

echo "🚀 Iniciando aplicación en Railway..."

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

# Obtener el puerto de Railway
PORT=${PORT:-3000}
echo "🌐 Puerto: $PORT"

# Iniciar la aplicación
echo "🚀 Iniciando aplicación..."
exec python test_app.py
