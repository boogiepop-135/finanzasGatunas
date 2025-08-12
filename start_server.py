#!/usr/bin/env python3
"""
Servidor de producción para Finanzas Gatunas
Compatible con Railway y otros servicios de deployment
"""
import os
import sys
from pathlib import Path

def main():
    # Configurar variables de entorno para producción
    os.environ.setdefault('FLASK_APP', 'src/app.py')
    os.environ.setdefault('FLASK_DEBUG', '0')
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Obtener puerto del entorno o usar 8080 por defecto (Railway usa PORT)
    port = int(os.environ.get('PORT', 8080))
    
    # Importar la aplicación
    sys.path.insert(0, str(script_dir / 'src'))
    from wsgi import application
    
    # Usar waitress en Windows, gunicorn en Linux
    if os.name == 'nt':  # Windows
        try:
            from waitress import serve
            print(f"🐱 Finanzas Gatunas iniciando en puerto {port} con Waitress...")
            serve(application, host='0.0.0.0', port=port, threads=4)
        except ImportError:
            print("Error: waitress no está instalado. Usar: pip install waitress")
            sys.exit(1)
    else:  # Linux/Unix (Railway)
        try:
            # En Railway, usar gunicorn directamente
            import subprocess
            cmd = [
                'gunicorn', 
                'wsgi:application',
                '--chdir', './src/',
                '--bind', f'0.0.0.0:{port}',
                '--workers', '2',
                '--timeout', '30',
                '--keep-alive', '2',
                '--max-requests', '1000',
                '--max-requests-jitter', '50',
                '--preload'
            ]
            print(f"🐱 Finanzas Gatunas iniciando en puerto {port} con Gunicorn...")
            subprocess.run(cmd)
        except Exception as e:
            print(f"Error iniciando con gunicorn: {e}")
            # Fallback a Flask dev server
            from src.app import app
            app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
