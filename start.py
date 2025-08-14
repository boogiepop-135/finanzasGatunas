#!/usr/bin/env python3
"""
Script de inicio para Railway
"""
import os
import subprocess
import sys

def main():
    print("🚀 Iniciando aplicación en Railway...")
    print(f"📅 Puerto: {os.environ.get('PORT', '3000')}")
    print(f"🔧 Directorio actual: {os.getcwd()}")
    print(f"📁 Archivos disponibles:")
    
    try:
        subprocess.run(["ls", "-la"], check=True)
    except:
        print("No se pudo listar archivos")
    
    print("🚀 Ejecutando gunicorn...")
    
    # Ejecutar gunicorn directamente
    try:
        subprocess.run([
            sys.executable, "-m", "gunicorn", 
            "-c", "gunicorn.conf.py", 
            "wsgi:app"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando gunicorn: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Aplicación interrumpida")
        sys.exit(0)

if __name__ == "__main__":
    main()
