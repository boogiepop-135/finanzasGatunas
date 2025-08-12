#!/bin/bash

# Script para construir la aplicación en Railway
echo "Iniciando script personalizado de construcción para Railway"

# Asegurarse de que estamos en la raíz del proyecto
cd /app

# Mostrar el directorio actual y su contenido
echo "Directorio actual:"
pwd
echo "Contenido del directorio:"
ls -la

# Verificar si index.html existe
if [ -f "index.html" ]; then
    echo "index.html encontrado"
else
    echo "index.html NO encontrado - esto es un problema"
fi

# Configurar variables de entorno para producción
if [ -f ".env.production" ]; then
    cp .env.production .env
else
    echo "NODE_ENV=production" > .env
    echo "FLASK_ENV=production" >> .env
    echo "FLASK_DEBUG=0" >> .env
    echo "VITE_BACKEND_URL=/api" >> .env
fi
export NODE_ENV=production
export VITE_BACKEND_URL=/api

# Mostrar la configuración de Vite
echo "Contenido de vite.config.js:"
cat vite.config.js

# Crear un archivo .env.local con la configuración necesaria
echo "Creando archivo .env.local para la construcción..."
echo "VITE_BACKEND_URL=/api" > .env.local

# Limpiar el directorio dist si existe
if [ -d "dist" ]; then
    echo "Limpiando directorio dist existente..."
    rm -rf dist
fi

# Intentar construir el frontend con la variable de entorno establecida
echo "Intentando construir la aplicación..."
VITE_BACKEND_URL=/api npm run build

# Verificar si la construcción fue exitosa
if [ $? -eq 0 ]; then
    echo "✅ Construcción del frontend exitosa!"
    echo "Contenido del directorio dist:"
    ls -la dist/ || echo "Directorio dist no encontrado"
else
    echo "❌ La construcción del frontend falló"
    exit 1
fi

echo "Fin del script de construcción"
