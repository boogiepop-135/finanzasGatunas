#!/usr/bin/env python3
"""
Aplicación de prueba ultra simple para Railway
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Hola! La aplicación está funcionando! 🐱"

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': '¡Funciona!'
    })

@app.route('/test')
def test():
    return jsonify({
        'message': 'Test exitoso',
        'port': os.environ.get('PORT', 'No definido')
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Iniciando aplicación de prueba en puerto {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🔍 Health: http://localhost:{port}/health")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Error: {e}")
        # Intentar puerto alternativo
        try:
            port = 8080
            print(f"🔄 Intentando puerto {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as e2:
            print(f"❌ Error fatal: {e2}")
            exit(1)
