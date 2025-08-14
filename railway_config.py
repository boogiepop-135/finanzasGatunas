"""
Configuración específica para Railway
"""
import os
from urllib.parse import urlparse

class RailwayConfig:
    """Configuración optimizada para Railway"""
    
    # Configuración de la base de datos
    @staticmethod
    def get_database_url():
        """Obtiene la URL de la base de datos para Railway"""
        database_url = os.environ.get('DATABASE_URL')
        
        if database_url:
            # Railway proporciona DATABASE_URL en formato postgresql://
            # Si es necesario, convertir a formato compatible
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        else:
            # Fallback a SQLite para desarrollo local
            return 'sqlite:///finanzas_gatunas.db'
    
    # Configuración de Flask
    @staticmethod
    def get_flask_config():
        """Obtiene la configuración de Flask para Railway"""
        return {
            'SQLALCHEMY_DATABASE_URI': RailwayConfig.get_database_url(),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'production'),
            'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        }
    
    # Configuración de CORS
    @staticmethod
    def get_cors_config():
        """Obtiene la configuración de CORS para Railway"""
        cors_origins = os.environ.get('CORS_ORIGINS', '*')
        if cors_origins == '*':
            return {'origins': '*'}
        else:
            return {'origins': cors_origins.split(',')}
    
    # Verificar si estamos en Railway
    @staticmethod
    def is_railway():
        """Verifica si la aplicación está ejecutándose en Railway"""
        return bool(os.environ.get('RAILWAY_ENVIRONMENT'))
    
    # Obtener puerto para Railway
    @staticmethod
    def get_port():
        """Obtiene el puerto para Railway"""
        return int(os.environ.get('PORT', 3000))

