# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Node.js dependencies (with --force para evitar conflictos)
RUN npm install --force

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Build frontend
RUN ls -la && \
    echo "Contenido de vite.config.js:" && \
    cat vite.config.js && \
    echo "Intentando construir la aplicación..." && \
    cp .env.production .env && \
    export NODE_ENV=production && \
    npm run build || echo "La construcción frontend falló pero continuaremos"

# Create database tables
RUN python -c "import os; os.environ['FLASK_APP']='src/app.py'; from src.app import app; from src.api.models import db; app.app_context().push(); db.create_all()" || echo "Database setup will be done at runtime"

# Expose port
EXPOSE $PORT

# Start command
CMD gunicorn wsgi --chdir ./src/ --bind 0.0.0.0:$PORT
