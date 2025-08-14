#!/bin/bash

echo "🚀 Build mínimo para Railway..."

# Build del frontend
npm run build

# Instalar Python dependencies
pip install flask

echo "✅ Build mínimo completado!"
