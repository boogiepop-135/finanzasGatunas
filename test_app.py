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
    # Obtener puerto de Railway
    port = int(os.environ.get('PORT', 3000))
    
    print("🚀 Iniciando aplicación de prueba en Railway...")
    print(f"📅 Python version: {sys.version}")
    print(f"🌐 Puerto: {port}")
    print(f"🔍 Health: http://localhost:{port}/health")
    print(f"🧪 Test: http://localhost:{port}/test")
    print(f"🏠 Home: http://localhost:{port}/")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Error al iniciar en puerto {port}: {e}")
        # Intentar puerto alternativo
        try:
            port = 8080
            print(f"🔄 Intentando puerto {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as e2:
            print(f"❌ Error fatal: {e2}")
            sys.exit(1)
