#!/usr/bin/env python3
"""
Archivo de prueba para verificar importaciones
"""
try:
    from app import app
    print("✅ Importación de app exitosa")
    print(f"   Tipo de app: {type(app)}")
    print(f"   App es Flask: {hasattr(app, 'route')}")
except ImportError as e:
    print(f"❌ Error importando app: {e}")

try:
    from wsgi import application
    print("✅ Importación de wsgi.application exitosa")
    print(f"   Tipo de application: {type(application)}")
    print(f"   Application es Flask: {hasattr(application, 'route')}")
except ImportError as e:
    print(f"❌ Error importando wsgi.application: {e}")

print("🔍 Prueba de importaciones completada")
