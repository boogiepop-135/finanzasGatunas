#!/usr/bin/env python3
"""
Script de inicio robusto para Railway
"""
import os
import sys
import time
import traceback

def main():
    print("🚀 Iniciando Finanzas Gatunas en Railway...")
    print(f"📅 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Entorno: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    print(f"🌍 Puerto: {os.environ.get('PORT', '3000')}")
    
    # Verificar archivos críticos
    critical_files = ['dist', 'dist/index.html']
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} existe")
        else:
            print(f"❌ {file_path} NO existe")
    
    # Intentar importar Flask
    try:
        from flask import Flask, send_from_directory, jsonify
        print("✅ Flask importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Flask: {e}")
        return 1
    
    # Crear aplicación simple
    try:
        app = Flask(__name__)
        print("✅ Aplicación Flask creada")
    except Exception as e:
        print(f"❌ Error creando aplicación: {e}")
        return 1
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Ruta de health check
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Finanzas Gatunas está funcionando en Railway! 🐱',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'port': os.environ.get('PORT', '3000')
        })
    
    # Ruta de prueba
    @app.route('/test')
    def test():
        return jsonify({
            'message': '¡La aplicación está funcionando!',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
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
            print(f"⚠️ Error sirviendo {path}: {e}")
            return f"Error: {str(e)}", 500
    
    # Iniciar aplicación
    try:
        port = int(os.environ.get('PORT', 3000))
        print(f"🚀 Iniciando aplicación en puerto {port}")
        print(f"🌐 URL: http://localhost:{port}")
        print(f"🔍 Health check: http://localhost:{port}/health")
        print(f"🧪 Test: http://localhost:{port}/test")
        
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Error al iniciar en puerto {port}: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        
        # Fallback: intentar puerto alternativo
        try:
            port = 8080
            print(f"🔄 Intentando puerto alternativo: {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as e2:
            print(f"❌ Error fatal en puerto {port}: {e2}")
            print(f"📋 Traceback: {traceback.format_exc()}")
            return 1
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal no manejado: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)
