#!/usr/bin/env python3
"""
Script de inicio con Gunicorn para Railway
"""
import os
import sys
import subprocess

def main():
    print("🚀 Iniciando con Gunicorn...")
    
    # Verificar que Gunicorn esté instalado
    try:
        import gunicorn
        print("✅ Gunicorn disponible")
    except ImportError:
        print("❌ Gunicorn no disponible, instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "gunicorn"], check=True)
    
    # Configuración de Gunicorn
    port = os.environ.get('PORT', '3000')
    workers = os.environ.get('GUNICORN_WORKERS', '1')
    
    # Comando de Gunicorn
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--workers', workers,
        '--timeout', '120',
        '--keep-alive', '5',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--preload',
        'test_app:app'
    ]
    
    print(f"🌍 Puerto: {port}")
    print(f"👥 Workers: {workers}")
    print(f"🔧 Comando: {' '.join(cmd)}")
    
    # Ejecutar Gunicorn
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error con Gunicorn: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por el usuario")
        return 0
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
