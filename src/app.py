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
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../dist/')
app = Flask(__name__)
app.url_map.strict_slashes = False

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

# Ruta específica para archivos estáticos en /assets/
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_path = os.path.join(static_file_dir, 'assets')
    
    if ENV == "development":
        print(f"Sirviendo asset: assets/{filename}")
        print(f"Ruta assets: {assets_path}")
    
    try:
        # Establecer tipos MIME para assets
        mimetype = None
        if filename.endswith('.js'):
            mimetype = 'application/javascript'
        elif filename.endswith('.css'):
            mimetype = 'text/css'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif filename.endswith('.svg'):
            mimetype = 'image/svg+xml'
        elif filename.endswith('.woff'):
            mimetype = 'font/woff'
        elif filename.endswith('.woff2'):
            mimetype = 'font/woff2'
        elif filename.endswith('.ttf'):
            mimetype = 'font/ttf'
        
        response = send_from_directory(assets_path, filename, mimetype=mimetype)
        # Cache largo para assets con hash en el nombre
        response.cache_control.max_age = 31536000  # 1 año
        return response
        
    except Exception as e:
        if ENV == "development":
            print(f"Error sirviendo asset {filename}: {e}")
        return f"Asset not found: {filename}", 404

# Ruta específica para el favicon
@app.route('/4geeks.ico')
def serve_favicon():
    try:
        response = send_from_directory(static_file_dir, '4geeks.ico', mimetype='image/x-icon')
        response.cache_control.max_age = 86400  # 1 día
        return response
    except Exception as e:
        if ENV == "development":
            print(f"Error sirviendo favicon: {e}")
        return "Favicon not found", 404

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    # Normalizar la ruta para evitar problemas con barras
    path = path.replace('\\', '/')
    full_path = os.path.join(static_file_dir, path)
    
    # Log para debugging en development
    if ENV == "development":
        print(f"Solicitando archivo: {path}")
        print(f"Ruta completa: {full_path}")
        print(f"Static dir: {static_file_dir}")
        print(f"Archivo existe: {os.path.isfile(full_path)}")
    
    # Verificar si el archivo existe
    if os.path.isfile(full_path):
        # El archivo existe, servirlo directamente
        try:
            # Establecer tipos MIME correctos
            mimetype = None
            if path.endswith('.js'):
                mimetype = 'application/javascript'
            elif path.endswith('.css'):
                mimetype = 'text/css'
            elif path.endswith('.html'):
                mimetype = 'text/html'
            elif path.endswith('.ico'):
                mimetype = 'image/x-icon'
            elif path.endswith('.png'):
                mimetype = 'image/png'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                mimetype = 'image/jpeg'
            elif path.endswith('.svg'):
                mimetype = 'image/svg+xml'
            elif path.endswith('.woff') or path.endswith('.woff2'):
                mimetype = 'font/woff' if path.endswith('.woff') else 'font/woff2'
            elif path.endswith('.ttf'):
                mimetype = 'font/ttf'
            
            response = send_from_directory(static_file_dir, path, mimetype=mimetype)
            
            # Cache control para assets
            if path.startswith('assets/') or path.endswith(('.js', '.css', '.png', '.jpg', '.ico')):
                response.cache_control.max_age = 31536000  # 1 año para assets con hash
            else:
                response.cache_control.max_age = 0  # Sin cache para index.html
                
            return response
            
        except Exception as e:
            if ENV == "development":
                print(f"Error sirviendo archivo {path}: {e}")
            return f"Error serving file: {path}", 500
    
    else:
        # El archivo no existe
        if ENV == "development":
            print(f"Archivo {path} no encontrado")
        
        # Para assets específicos que no existen, devolver 404
        asset_extensions = ['.js', '.css', '.ico', '.png', '.jpg', '.jpeg', '.svg', '.woff', '.woff2', '.ttf', '.map']
        if any(path.endswith(ext) for ext in asset_extensions):
            if ENV == "development":
                print(f"Asset {path} no encontrado, devolviendo 404")
            return f"Asset not found: {path}", 404
        
        # Para rutas de navegación SPA, servir index.html
        try:
            if ENV == "development":
                print(f"Ruta de navegación {path}, sirviendo index.html")
            
            response = send_from_directory(static_file_dir, 'index.html', mimetype='text/html')
            response.cache_control.max_age = 0  # Sin cache para navegación SPA
            return response
            
        except Exception as e:
            if ENV == "development":
                print(f"Error crítico sirviendo index.html: {e}")
            return f"Server error: cannot serve {path}", 500


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=False)
