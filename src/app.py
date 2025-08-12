"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from pathlib import Path
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

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"

# SOLUCION DEFINITIVA: Usar Path para rutas absolutas
current_dir = Path(__file__).parent
project_root = current_dir.parent
static_file_dir = project_root / 'dist'

print(f"[APP] Environment: {ENV}")
print(f"[APP] Current dir: {current_dir}")
print(f"[APP] Project root: {project_root}")
print(f"[APP] Static dir: {static_file_dir}")
print(f"[APP] Static dir exists: {static_file_dir.exists()}")

app = Flask(__name__, static_folder=str(static_file_dir), static_url_path='')
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

@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(str(static_file_dir), 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    """Servir archivos estáticos o SPA routing"""
    try:
        file_path = static_file_dir / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(str(static_file_dir), path)
        elif path.endswith(('.js', '.css', '.png', '.jpg', '.ico', '.svg')):
            return f"File not found: {path}", 404
        else:
            # SPA fallback
            return send_from_directory(str(static_file_dir), 'index.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=False)
