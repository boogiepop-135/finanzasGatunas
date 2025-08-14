#!/bin/bash
echo "🚀 Iniciando aplicación Python con Gunicorn..."
gunicorn -c gunicorn.conf.py wsgi:app
