#!/usr/bin/env python3
"""
Archivo WSGI para Railway
"""
from app import app

# Variable estándar que gunicorn busca
application = app

if __name__ == "__main__":
    app.run()
