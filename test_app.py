#!/usr/bin/env python3
"""
Aplicación de prueba ultra simple para Railway
"""
import os
import sys
from flask import Flask, jsonify

app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def home():
    return "¡Hola! La aplicación está funcionando! 🐱"

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': '¡Funciona!',
        'port': os.environ.get('PORT', 'No definido'),
        'environment': 'Railway'
    })

@app.route('/test')
def test():
    return jsonify({
        'message': 'Test exitoso',
        'port': os.environ.get('PORT', 'No definido'),
        'python_version': sys.version,
        'flask_version': '3.1.1'
    })

if __name__ == '__main__':
    # Obtener puerto de Railway (es obligatorio)
    port_str = os.environ.get('PORT')
    if not port_str:
        print("❌ Error: Variable PORT no está definida")
        print("🔍 Variables de entorno disponibles:")
        for key, value in os.environ.items():
            print(f"   {key}: {value}")
        sys.exit(1)
    
    try:
        port = int(port_str)
    except ValueError:
        print(f"❌ Error: Puerto '{port_str}' no es válido")
        sys.exit(1)
    
    print("🚀 Iniciando aplicación de prueba en Railway...")
    print(f"📅 Python version: {sys.version}")
    print(f"🌐 Puerto: {port}")
    print(f"🔍 Health: http://localhost:{port}/health")
    print(f"🧪 Test: http://localhost:{port}/test")
    print(f"🏠 Home: http://localhost:{port}/")
    print(f"🔧 Variables de entorno:")
    print(f"   PORT: {os.environ.get('PORT')}")
    print(f"   RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'No definido')}")
    
    try:
        print(f"🚀 Iniciando Flask en 0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Error al iniciar en puerto {port}: {e}")
        print(f"📋 Traceback completo:")
        import traceback
        traceback.print_exc()
        
        # Intentar puerto alternativo
        try:
            port = 8080
            print(f"🔄 Intentando puerto alternativo: {port}")
            app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        except Exception as e2:
            print(f"❌ Error fatal en puerto {port}: {e2}")
            print(f"📋 Traceback completo:")
            traceback.print_exc()
            sys.exit(1)
