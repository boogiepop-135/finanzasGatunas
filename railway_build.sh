#!/usr/bin/env bash
# Railway build script for Finanzas Gatunas
set -o errexit

echo "🐱 Building Finanzas Gatunas..."

# Install Node.js dependencies and build frontend
echo "📦 Installing Node.js dependencies..."
npm install

echo "🏗️ Building React frontend..."
npm run build

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Setting up database..."
python -c "
import os
os.environ['FLASK_APP'] = 'src/app.py'
from src.app import app
from src.api.models import db
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"

echo "✅ Build completed successfully!"
