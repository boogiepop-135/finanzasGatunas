"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from dotenv import load_dotenv
from api.utils import APIException, generate_sitemap
from api.models import db
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands

# Load environment variables
load_dotenv()

# from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"

# Configurar directorio estático según el entorno
if ENV == "development":
    static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../dist')
    app = Flask(__name__, static_folder='../dist', static_url_path='')
else:
    # En producción (Railway), el directorio dist está en el nivel raíz
    static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../dist')
    app = Flask(__name__, static_folder='../dist', static_url_path='')

app.url_map.strict_slashes = False

# Log para debugging en producción
print(f"[INIT] Environment: {ENV}")
print(f"[INIT] Static file directory: {static_file_dir}")
print(f"[INIT] Static dir exists: {os.path.exists(static_file_dir)}")
if os.path.exists(static_file_dir):
    print(f"[INIT] Static dir contents: {os.listdir(static_file_dir)}")
    assets_dir = os.path.join(static_file_dir, 'assets')
    if os.path.exists(assets_dir):
        print(f"[INIT] Assets dir contents: {os.listdir(assets_dir)}")
print(f"[INIT] Current working directory: {os.getcwd()}")
print(f"[INIT] App static folder: {app.static_folder}")
print(f"[INIT] App static url path: {app.static_url_path}")

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    print(f"[SERVE] Requested path: {path}")
    print(f"[SERVE] Static dir: {static_file_dir}")
    
    try:
        # Intentar servir el archivo desde el directorio static
        full_path = os.path.join(static_file_dir, path)
        print(f"[SERVE] Full path: {full_path}")
        print(f"[SERVE] File exists: {os.path.exists(full_path)}")
        
        if os.path.exists(full_path):
            # Establecer tipos MIME apropiados
            mimetype = None
            if path.endswith('.css'):
                mimetype = 'text/css'
            elif path.endswith('.js'):
                mimetype = 'application/javascript'
            elif path.endswith('.ico'):
                mimetype = 'image/x-icon'
            
            print(f"[SERVE] Serving with mimetype: {mimetype}")
            response = send_from_directory(static_file_dir, path, mimetype=mimetype)
            return response
        else:
            print(f"[SERVE] File not found: {path}")
            return send_from_directory(static_file_dir, path)
            
    except Exception as e:
        print(f"[SERVE] Exception: {str(e)}")
        # Si no se encuentra, verificar si es una ruta de asset
        if path.startswith('assets/') or path.endswith(('.js', '.css', '.png', '.jpg', '.ico', '.svg')):
            # Es un asset que no existe, devolver 404
            print(f"[SERVE] Asset not found: {path}")
            return f"File not found: {path}", 404
        else:
            # Es una ruta de navegación SPA, servir index.html
            try:
                print(f"[SERVE] Serving index.html for SPA route: {path}")
                return send_from_directory(static_file_dir, 'index.html')
            except Exception as e2:
                print(f"[SERVE] Failed to serve index.html: {str(e2)}")
                return "Application not found", 404


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=False)
