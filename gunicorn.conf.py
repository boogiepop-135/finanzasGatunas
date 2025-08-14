#!/usr/bin/env python3
"""
Configuración de Gunicorn para Railway
"""
import os

# Configuración del servidor
bind = f"0.0.0.0:{os.environ.get('PORT', '3000')}"
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Configuración de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configuración de la aplicación
preload_app = True
max_requests = 1000
max_requests_jitter = 100

# No cambiar de directorio
chdir = None
