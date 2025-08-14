#!/bin/bash

echo "🚀 Iniciando build para Railway..."

# Instalar dependencias
echo "📦 Instalando dependencias..."
npm install

# Construir el frontend
echo "🔨 Construyendo el frontend..."
npm run build

# Verificar que el build se completó
if [ ! -d "dist" ]; then
    echo "❌ Error: El directorio dist no se creó"
    exit 1
fi

echo "✅ Build completado exitosamente!"
echo "📁 Contenido del directorio dist:"
ls -la dist/

# Instalar dependencias de Python
echo "🐍 Instalando dependencias de Python..."
pip install -r requirements.txt

echo "✅ Script de build completado!"
echo "🚀 La aplicación está lista para ejecutarse con: python railway_app.py"
