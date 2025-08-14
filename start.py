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
    
    # Ejecutar gunicorn directamente
    try:
        print("🚀 Ejecutando gunicorn...")
        subprocess.run([
            sys.executable, "-m", "gunicorn", 
            "--bind", f"0.0.0.0:{os.environ.get('PORT', '3000')}",
            "--workers", "1",
            "--timeout", "30",
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
