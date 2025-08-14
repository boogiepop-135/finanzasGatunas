#!/usr/bin/env python3
"""
Aplicación principal para Railway - Finanzas Gatunas
"""
from flask import Flask, jsonify, render_template_string
import os
from datetime import datetime

app = Flask(__name__)

# HTML template para la página principal
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐱 Finanzas Gatunas - Railway</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .status-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        
        .status-card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 2rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #4CAF50;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .info-card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            color: white;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .info-card h3 {
            margin-bottom: 15px;
            color: #fff;
        }
        
        .info-card p {
            opacity: 0.9;
            line-height: 1.6;
        }
        
        .routes-list {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .routes-list h3 {
            color: #667eea;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .route-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .route-path {
            font-family: monospace;
            font-weight: bold;
            color: #667eea;
        }
        
        .route-description {
            color: #666;
        }
        
        .timestamp {
            text-align: center;
            color: rgba(255,255,255,0.7);
            margin-top: 20px;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐱 Finanzas Gatunas</h1>
            <p>Tu aplicación está funcionando perfectamente en Railway</p>
        </div>
        
        <div class="status-card">
            <h2>Estado del Sistema</h2>
            <p><span class="status-indicator"></span> Aplicación funcionando correctamente</p>
            <p>Puerto: {{ port }}</p>
            <p>Entorno: {{ environment }}</p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>🚀 Railway</h3>
                <p>Tu aplicación está desplegada exitosamente en Railway. El sistema está funcionando sin problemas.</p>
            </div>
            
            <div class="info-card">
                <h3>🐍 Python + Flask</h3>
                <p>Backend construido con Python 3.11 y Flask. Gunicorn está sirviendo la aplicación correctamente.</p>
            </div>
            
            <div class="info-card">
                <h3>🔧 Configuración</h3>
                <p>La aplicación está configurada para funcionar en Railway con healthchecks automáticos y reinicio automático.</p>
            </div>
        </div>
        
        <div class="routes-list">
            <h3>📡 Rutas Disponibles</h3>
            <div class="route-item">
                <span class="route-path">/</span>
                <span class="route-description">Página principal (esta página)</span>
            </div>
            <div class="route-item">
                <span class="route-path">/health</span>
                <span class="route-description">Healthcheck para Railway</span>
            </div>
            <div class="route-item">
                <span class="route-path">/test</span>
                <span class="route-description">Ruta de prueba API</span>
            </div>
            <div class="route-item">
                <span class="route-path">/api/status</span>
                <span class="route-description">Estado del sistema en JSON</span>
            </div>
        </div>
        
        <div class="timestamp">
            Última actualización: {{ timestamp }}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Página principal con interfaz HTML atractiva"""
    return render_template_string(MAIN_PAGE_HTML, 
                                port=os.environ.get('PORT', '3000'),
                                environment=os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
                                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))

@app.route('/health')
def health():
    """Healthcheck para Railway"""
    return jsonify({
        'status': 'healthy',
        'message': '¡Aplicación funcionando perfectamente! 🐱',
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
        'port': os.environ.get('PORT', '3000')
    })

@app.route('/test')
def test():
    """Ruta de prueba API"""
    return jsonify({
        'message': 'Test exitoso',
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """Estado completo del sistema"""
    return jsonify({
        'application': 'Finanzas Gatunas',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
        'port': os.environ.get('PORT', '3000'),
        'python_version': '3.11',
        'framework': 'Flask',
        'server': 'Gunicorn',
        'deployment': 'Railway',
        'health': 'healthy'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Iniciando aplicación en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
