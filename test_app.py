#!/usr/bin/env python3
"""
Aplicación de prueba ultra simple para Railway
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Hola! La aplicación está funcionando! 🐱"

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': '¡Funciona!',
        'port': os.environ.get('PORT', 'No definido')
    })

@app.route('/test')
def test():
    return jsonify({
        'message': 'Test exitoso',
        'port': os.environ.get('PORT', 'No definido')
    })

if __name__ == '__main__':
    # Obtener puerto de Railway
    port = int(os.environ.get('PORT', 3000))
    
    print(f"🚀 Iniciando aplicación en puerto {port}")
    print(f"🔍 Health: http://localhost:{port}/health")
    
    # Iniciar aplicación
    app.run(host='0.0.0.0', port=port, debug=False)
