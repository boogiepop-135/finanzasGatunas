#!/bin/bash

echo "🚀 Build simple para Railway..."

# Instalar Node.js dependencies
npm install

# Build del frontend
npm run build

# Instalar Python dependencies
pip install -r requirements.txt

echo "✅ Build completado!"
