#!/usr/bin/env python3
"""
Aplicación principal para Railway que sirve tanto la API como el frontend compilado
"""
import os
import sys
from pathlib import Path

# Agregar el directorio src al path para importar la API
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, send_from_directory, request, jsonify
from api.routes import api
from api.models import db
from api.admin import admin_bp
from railway_config import RailwayConfig

app = Flask(__name__)

# Aplicar configuración de Railway
app.config.update(RailwayConfig.get_flask_config())

# Inicializar la base de datos
db.init_app(app)

# Registrar blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Ruta de health check para Railway
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Finanzas Gatunas está funcionando correctamente en Railway! 🐱',
        'environment': 'Railway' if RailwayConfig.is_railway() else 'Local',
        'database': 'PostgreSQL' if 'postgresql' in RailwayConfig.get_database_url() else 'SQLite'
    })

# Servir archivos estáticos del build de Vite
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Si la ruta es para la API o admin, no servir archivos estáticos
    if path.startswith('api/') or path.startswith('admin/'):
        return "Not Found", 404
    
    # Verificar si el archivo existe en dist
    dist_path = os.path.join('dist', path)
    if path != "" and os.path.exists(dist_path):
        return send_from_directory('dist', path)
    else:
        # Para rutas del SPA, servir siempre index.html
        return send_from_directory('dist', 'index.html')

# Crear las tablas de la base de datos si no existen
@app.before_first_request
def create_tables():
    try:
        with app.app_context():
            db.create_all()
            print("✅ Tablas de la base de datos creadas exitosamente!")
            print(f"🗄️ Base de datos: {RailwayConfig.get_database_url()}")
    except Exception as e:
        print(f"⚠️ Error al crear tablas: {e}")

if __name__ == '__main__':
    port = RailwayConfig.get_port()
    print(f"🚀 Iniciando Finanzas Gatunas en puerto {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🏗️ Entorno: {'Railway' if RailwayConfig.is_railway() else 'Local'}")
    app.run(host='0.0.0.0', port=port, debug=RailwayConfig.get_flask_config()['FLASK_DEBUG'])
