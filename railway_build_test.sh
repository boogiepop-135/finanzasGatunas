#!/bin/bash

echo "🚀 Build de prueba para Railway..."

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cat > .env << EOF
NODE_ENV=production
VITE_BACKEND_URL=/api
FLASK_ENV=production
FLASK_DEBUG=false
EOF
fi

# Instalar dependencias de Node.js
echo "📦 Instalando dependencias de Node.js..."
npm install

# Construir el frontend
echo "🔨 Construyendo el frontend..."
npm run build

# Verificar que el build se completó
if [ ! -d "dist" ]; then
    echo "❌ Error: El directorio dist no se creó"
    exit 1
fi

echo "✅ Frontend construido exitosamente!"

# Instalar solo Flask para la app de prueba
echo "🐍 Instalando Flask..."
pip install flask

echo "✅ Build de prueba completado!"
echo "📁 Contenido del directorio dist:"
ls -la dist/
