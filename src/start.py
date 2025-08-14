#!/usr/bin/env python3
"""
Script de inicio para Railway (desde directorio src)
"""
import os
import subprocess
import sys

def main():
    print("🚀 Iniciando aplicación en Railway desde src...")
    print(f"📅 Puerto: {os.environ.get('PORT', '3000')}")
    print(f"🔧 Directorio actual: {os.getcwd()}")
    
    # Ejecutar gunicorn directamente desde src
    try:
        print("🚀 Ejecutando gunicorn desde src...")
        subprocess.run([
            sys.executable, "-m", "gunicorn", 
            "--bind", f"0.0.0.0:{os.environ.get('PORT', '3000')}",
            "--workers", "1",
            "--timeout", "30",
            "wsgi:application"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando gunicorn: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Aplicación interrumpida")
        sys.exit(0)

if __name__ == "__main__":
    main()
