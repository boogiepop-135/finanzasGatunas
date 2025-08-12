#!/bin/bash
# Setup script for Railway

echo "Setting up Finanzas Gatunas..."

# Build frontend
npm run build

# Setup database
python -c "
import os
import sys
import subprocess

# Ensure we're in the right directory
os.chdir('/app')
sys.path.insert(0, 'src')

try:
    from app import app
    from api.models import db
    
    with app.app_context():
        db.create_all()
        print('Database setup complete!')
except Exception as e:
    print(f'Database setup error: {e}')
"

echo "Setup complete!"
