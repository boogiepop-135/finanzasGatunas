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

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    full_path = os.path.join(static_file_dir, path)
    
    # Log para debugging
    print(f"Solicitando archivo: {path}")
    print(f"Ruta completa: {full_path}")
    print(f"Archivo existe: {os.path.isfile(full_path)}")
    
    # Si el archivo no existe y es un asset específico (.js, .css, .ico, etc), devolver 404
    # Solo servir index.html para rutas de navegación (SPA routing)
    if not os.path.isfile(full_path):
        print(f"Archivo {path} no encontrado")
        
        # No servir index.html para assets específicos que no existen
        if (path.endswith('.js') or path.endswith('.css') or 
            path.endswith('.ico') or path.endswith('.png') or 
            path.endswith('.jpg') or path.endswith('.jpeg') or
            path.endswith('.svg') or path.endswith('.woff') or 
            path.endswith('.woff2') or path.endswith('.ttf')):
            print(f"Asset {path} no encontrado, devolviendo 404")
            return f"Asset not found: {path}", 404
        
        # Para rutas de navegación, servir index.html (SPA routing)
        print(f"Ruta de navegación {path}, sirviendo index.html")
        path = 'index.html'
    
    # Establecer los tipos MIME correctos
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
    
    try:
        response = send_from_directory(static_file_dir, path, mimetype=mimetype)
        response.cache_control.max_age = 0  # avoid cache memory
        return response
    except Exception as e:
        print(f"Error sirviendo archivo {path}: {e}")
        # Si hay cualquier error y no es un asset específico, intentar servir index.html
        if not (path.endswith('.js') or path.endswith('.css') or path.endswith('.ico')):
            try:
                return send_from_directory(static_file_dir, 'index.html', mimetype='text/html')
            except Exception as e2:
                print(f"Error crítico sirviendo index.html: {e2}")
                return f"Error del servidor: no se puede servir {path}", 500
        else:
            return f"Asset not found: {path}", 404


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=False)
