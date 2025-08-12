#!/usr/bin/env bash
# Post-install script for Railway deployment

echo "🐱 Setting up Finanzas Gatunas database..."

# Set Flask app environment variable
export FLASK_APP=src/app.py

# Create database tables
python -c "
import os
import sys
sys.path.insert(0, 'src')

try:
    from app import app
    from api.models import db
    
    with app.app_context():
        db.create_all()
        print('✅ Database tables created successfully!')
        
except Exception as e:
    print(f'❌ Error creating database: {e}')
    sys.exit(1)
"

echo "🎉 Finanzas Gatunas setup completed!"
