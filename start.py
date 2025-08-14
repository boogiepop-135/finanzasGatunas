#!/usr/bin/env python3
"""
Script de inicio simple para Railway
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
    
    print("🚀 Ejecutando test_app.py...")
    
    # Ejecutar la aplicación
    try:
        subprocess.run([sys.executable, "test_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando test_app.py: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Aplicación interrumpida")
        sys.exit(0)

if __name__ == "__main__":
    main()
