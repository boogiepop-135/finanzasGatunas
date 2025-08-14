#!/usr/bin/env python3
"""
Aplicación simplificada para Railway - Versión de emergencia
"""
import os
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ruta de health check simple
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Finanzas Gatunas está funcionando en Railway! 🐱',
        'port': os.environ.get('PORT', '3000')
    })

# Ruta de prueba
@app.route('/test')
def test():
    return jsonify({
        'message': '¡La aplicación está funcionando!',
        'timestamp': '2024-01-01'
    })

# Servir archivos estáticos
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    try:
        # Verificar si el archivo existe en dist
        dist_path = os.path.join('dist', path)
        if path != "" and os.path.exists(dist_path):
            return send_from_directory('dist', path)
        else:
            # Para rutas del SPA, servir index.html
            return send_from_directory('dist', 'index.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Iniciando aplicación en puerto {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🔍 Health check: http://localhost:{port}/health")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Error al iniciar: {e}")
        # Fallback: intentar con puerto alternativo
        try:
            port = 8080
            print(f"🔄 Intentando puerto alternativo: {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as e2:
            print(f"❌ Error fatal: {e2}")
            exit(1)
