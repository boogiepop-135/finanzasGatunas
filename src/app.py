#!/usr/bin/env python3
"""
Aplicación principal para Railway
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Hola! La aplicación está funcionando! 🐱"

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': '¡Funciona!'})

@app.route('/test')
def test():
    return jsonify({'message': 'Test exitoso'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Iniciando aplicación en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
