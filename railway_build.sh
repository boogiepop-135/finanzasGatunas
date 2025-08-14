#!/bin/bash

# Script de build optimizado para Railway
set -e  # Salir en caso de error

echo "🚀 Iniciando build para Railway..."
echo "📅 Fecha: $(date)"
echo "🔧 Entorno: $RAILWAY_ENVIRONMENT"

# Verificar que estamos en Railway
if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "✅ Ejecutando en Railway"
else
    echo "⚠️ Ejecutando en entorno local"
fi

# Limpiar directorios anteriores si existen
echo "🧹 Limpiando directorios anteriores..."
rm -rf node_modules dist

# Instalar dependencias de Node.js
echo "📦 Instalando dependencias de Node.js..."
npm ci --production=false --silent

# Verificar que npm install fue exitoso
if [ $? -ne 0 ]; then
    echo "❌ Error en npm install"
    exit 1
fi

# Construir el frontend
echo "🔨 Construyendo el frontend..."
npm run build

# Verificar que el build se completó
if [ ! -d "dist" ]; then
    echo "❌ Error: El directorio dist no se creó"
    exit 1
fi

echo "✅ Build del frontend completado exitosamente!"
echo "📁 Contenido del directorio dist:"
ls -la dist/

# Instalar dependencias de Python
echo "🐍 Instalando dependencias de Python..."
pip install --no-cache-dir -r requirements.txt

# Verificar que pip install fue exitoso
if [ $? -ne 0 ]; then
    echo "❌ Error en pip install"
    exit 1
fi

# Crear archivo de estado del build
echo "📝 Creando archivo de estado del build..."
cat > build_status.txt << EOF
Build completado: $(date)
Frontend: ✅
Python: ✅
Entorno: ${RAILWAY_ENVIRONMENT:-local}
EOF

echo "✅ Script de build completado exitosamente!"
echo "🚀 La aplicación está lista para ejecutarse con: python railway_app.py"
echo "📊 Estado del build guardado en build_status.txt"
