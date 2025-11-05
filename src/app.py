#!/usr/bin/env python3
"""
Aplicación de Finanzas del Hogar - Finanzas Gatunas
"""
from flask import Flask, jsonify, render_template_string, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import os
from datetime import datetime, timedelta
import json
import csv
from io import StringIO
import base64
import matplotlib
matplotlib.use('Agg')  # Para servidor sin GUI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import random
import string

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'finanzas-gatunas-secret-key')

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

# Configuración de MongoDB
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'finanzas_gatunas')

# Conectar a MongoDB
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGODB_DB_NAME]
    # Verificar conexión
    client.admin.command('ping')
    print(f"[OK] Conectado a MongoDB: {MONGODB_DB_NAME}")
except Exception as e:
    print(f"[ERROR] Error conectando a MongoDB: {e}")
    print(f"[INFO] La aplicacion seguira funcionando pero sin base de datos")
    db = None

# Clase User para Flask-Login
class User(UserMixin):
    def __init__(self, user_id, email, nombre, email_verificado=False):
        self.id = user_id
        self.email = email
        self.nombre = nombre
        self.email_verificado = email_verificado

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario desde MongoDB"""
    if db is None:
        return None
    try:
        user_doc = db.usuarios.find_one({'_id': ObjectId(user_id)})
        if user_doc:
            return User(
                str(user_doc['_id']),
                user_doc['email'],
                user_doc.get('nombre', ''),
                user_doc.get('email_verificado', False)
            )
    except:
        pass
    return None

def init_db():
    """Inicializar la base de datos con datos por defecto"""
    if db is None:
        return
    
    # Colecciones ya están creadas automáticamente en MongoDB
    # Solo necesitamos insertar datos por defecto si no existen
    
    # Insertar tarjetas por defecto
    if db.tarjetas.count_documents({}) == 0:
        tarjetas_default = [
            {
                'nombre': 'Efectivo',
                'tipo': 'efectivo',
                'banco': 'N/A',
                'limite_credito': 0,
                'fecha_vencimiento': None,
                'color': '#4CAF50',
                'icono': '💵',
                'activa': True,
                'created_at': datetime.now()
            },
            {
                'nombre': 'Débito Principal',
                'tipo': 'debito',
                'banco': 'Banco Local',
                'limite_credito': 0,
                'fecha_vencimiento': None,
                'color': '#2196F3',
                'icono': '🏦',
                'activa': True,
                'created_at': datetime.now()
            },
            {
                'nombre': 'Crédito Visa',
                'tipo': 'credito',
                'banco': 'Banco Principal',
                'limite_credito': 50000,
                'fecha_vencimiento': '2026-12-31',
                'color': '#9C27B0',
                'icono': '💳',
                'activa': True,
                'created_at': datetime.now()
            },
            {
                'nombre': 'Crédito Mastercard',
                'tipo': 'credito',
                'banco': 'Banco Secundario',
                'limite_credito': 30000,
                'fecha_vencimiento': '2026-06-30',
                'color': '#FF9800',
                'icono': '💳',
                'activa': True,
                'created_at': datetime.now()
            }
        ]
        db.tarjetas.insert_many(tarjetas_default)
    
    # Insertar categorías por defecto
    if db.categorias.count_documents({}) == 0:
        categorias_default = [
            {'nombre': 'Ingresos', 'tipo': 'ingreso', 'color': '#4CAF50', 'icono': '💰', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Salario', 'tipo': 'ingreso', 'color': '#4CAF50', 'icono': '💼', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Freelance', 'tipo': 'ingreso', 'color': '#4CAF50', 'icono': '💻', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Inversiones', 'tipo': 'ingreso', 'color': '#4CAF50', 'icono': '📈', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Alimentación', 'tipo': 'gasto', 'color': '#FF5722', 'icono': '🍽️', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Transporte', 'tipo': 'gasto', 'color': '#2196F3', 'icono': '🚗', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Vivienda', 'tipo': 'gasto', 'color': '#9C27B0', 'icono': '🏠', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Entretenimiento', 'tipo': 'gasto', 'color': '#FF9800', 'icono': '🎮', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Salud', 'tipo': 'gasto', 'color': '#E91E63', 'icono': '🏥', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Educación', 'tipo': 'gasto', 'color': '#607D8B', 'icono': '📚', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Ropa', 'tipo': 'gasto', 'color': '#795548', 'icono': '👕', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Membresías', 'tipo': 'gasto', 'color': '#FF5722', 'icono': '🎫', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Servicios', 'tipo': 'gasto', 'color': '#3F51B5', 'icono': '🔌', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()},
            {'nombre': 'Otros', 'tipo': 'gasto', 'color': '#9E9E9E', 'icono': '📦', 'presupuesto_mensual': 0, 'activa': True, 'created_at': datetime.now()}
        ]
        db.categorias.insert_many(categorias_default)
    
    # Insertar membresías de ejemplo
    if db.membresias.count_documents({}) == 0:
        # Obtener IDs de tarjetas
        tarjeta_ids = list(db.tarjetas.find({}, {'_id': 1}))
        if len(tarjeta_ids) >= 3:
            membresias_default = [
                {
                    'nombre': 'Netflix',
                    'plataforma': 'Netflix',
                    'tipo': 'streaming',
                    'monto_mensual': 15.99,
                    'monto_anual': 191.88,
                    'tarjeta_id': str(tarjeta_ids[2]['_id']),
                    'fecha_inicio': '2024-01-01',
                    'fecha_renovacion': '2024-02-01',
                    'estado': 'activa',
                    'notas': None,
                    'created_at': datetime.now()
                },
                {
                    'nombre': 'Spotify',
                    'plataforma': 'Spotify',
                    'tipo': 'musica',
                    'monto_mensual': 9.99,
                    'monto_anual': 119.88,
                    'tarjeta_id': str(tarjeta_ids[2]['_id']),
                    'fecha_inicio': '2024-01-01',
                    'fecha_renovacion': '2024-02-01',
                    'estado': 'activa',
                    'notas': None,
                    'created_at': datetime.now()
                },
                {
                    'nombre': 'Gym',
                    'plataforma': 'Local Gym',
                    'tipo': 'fitness',
                    'monto_mensual': 29.99,
                    'monto_anual': 359.88,
                    'tarjeta_id': str(tarjeta_ids[1]['_id']),
                    'fecha_inicio': '2024-01-01',
                    'fecha_renovacion': '2024-02-01',
                    'estado': 'activa',
                    'notas': None,
                    'created_at': datetime.now()
                }
            ]
            db.membresias.insert_many(membresias_default)

def convert_mongo_to_dict(item):
    """Convertir documento MongoDB a diccionario con id como string"""
    if item is None:
        return None
    try:
        doc = dict(item)
        if '_id' in doc:
            doc['id'] = str(doc.pop('_id'))
        return doc
    except Exception as e:
        print(f"[ERROR] Error convirtiendo documento MongoDB: {e}")
        return None

def convert_list_to_dicts(items):
    """Convertir lista de documentos MongoDB a lista de diccionarios"""
    resultado = []
    for item in items:
        try:
            converted = convert_mongo_to_dict(item)
            if converted:
                resultado.append(converted)
        except Exception as e:
            print(f"[ERROR] Error convirtiendo lista MongoDB: {e}")
            continue
    return resultado

# ===== FUNCIONES DE AUTENTICACIÓN Y VERIFICACIÓN =====

def generar_codigo_verificacion():
    """Generar código de verificación de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))

def enviar_codigo_verificacion(email, codigo):
    """Enviar código de verificación por email"""
    try:
        msg = Message(
            subject='Código de Verificación - Finanzas Gatunas',
            recipients=[email],
            html=f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">🐱 Finanzas Gatunas</h2>
                <p>Tu código de verificación es:</p>
                <div style="background: #667eea; color: white; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; border-radius: 10px; margin: 20px 0;">
                    {codigo}
                </div>
                <p>Este código expira en 15 minutos.</p>
                <p>Si no solicitaste este código, ignora este mensaje.</p>
            </body>
            </html>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[ERROR] Error enviando email: {e}")
        return False

def verificar_permiso(usuario_id, accion='ver'):
    """Verificar si el usuario tiene permiso para ver/editar"""
    if not current_user.is_authenticated:
        return False
    
    # El dueño siempre tiene todos los permisos
    if str(current_user.id) == str(usuario_id):
        return True
    
    # Verificar si hay una invitación activa
    if db is not None:
        invitacion = db.invitaciones.find_one({
            'usuario_invitado_id': str(current_user.id),
            'usuario_propietario_id': str(usuario_id),
            'estado': 'aceptada'
        })
        
        if invitacion:
            if accion == 'ver':
                return invitacion.get('permiso') in ['ver', 'editar']
            elif accion == 'editar':
                return invitacion.get('permiso') == 'editar'
    
    return False

def obtener_usuario_actual_id():
    """Obtener ID del usuario actual o None"""
    if current_user.is_authenticated:
        return str(current_user.id)
    return None

def obtener_finanzas_compartidas():
    """Obtener finanzas compartidas con el usuario actual"""
    if not current_user.is_authenticated or db is None:
        return []
    
    # Obtener invitaciones aceptadas donde el usuario es invitado
    invitaciones = list(db.invitaciones.find({
        'usuario_invitado_id': str(current_user.id),
        'estado': 'aceptada'
    }))
    
    resultado = []
    for inv in invitaciones:
        usuario_propietario = db.usuarios.find_one({'_id': ObjectId(inv['usuario_propietario_id'])})
        if usuario_propietario:
            resultado.append({
                'usuario_id': inv['usuario_propietario_id'],
                'email': usuario_propietario.get('email'),
                'nombre': usuario_propietario.get('nombre'),
                'permiso': inv.get('permiso', 'ver')
            })
    
    return resultado

def get_tarjetas(usuario_id=None):
    """Obtener todas las tarjetas del usuario"""
    if db is None:
        return []
    query = {'activa': True}
    if usuario_id:
        query['usuario_id'] = usuario_id
    tarjetas = list(db.tarjetas.find(query).sort('nombre', 1))
    return convert_list_to_dicts(tarjetas)

def get_membresias(usuario_id=None):
    """Obtener todas las membresías del usuario"""
    if db is None:
        return []
    query = {}
    if usuario_id:
        query['usuario_id'] = usuario_id
    membresias = list(db.membresias.find(query).sort('fecha_renovacion', 1))
    result = []
    for mem in membresias:
        mem_dict = convert_mongo_to_dict(mem)
        # Agregar información de tarjeta
        if mem_dict.get('tarjeta_id'):
            tarjeta = db.tarjetas.find_one({'_id': ObjectId(mem_dict['tarjeta_id'])})
            if tarjeta:
                mem_dict['tarjeta_nombre'] = tarjeta.get('nombre')
                mem_dict['tarjeta_color'] = tarjeta.get('color')
                mem_dict['tarjeta_icono'] = tarjeta.get('icono')
        result.append(mem_dict)
    return result

def get_presupuestos(mes=None, año=None, usuario_id=None):
    """Obtener presupuestos mensuales del usuario"""
    if db is None:
        return []
    query = {}
    if mes and año:
        query['mes'] = mes
        query['año'] = año
    if usuario_id:
        query['usuario_id'] = usuario_id
    
    presupuestos = list(db.presupuestos.find(query).sort([('año', -1), ('mes', -1), ('categoria_id', 1)]))
    result = []
    for pres in presupuestos:
        pres_dict = convert_mongo_to_dict(pres)
        # Agregar información de categoría
        if pres_dict.get('categoria_id'):
            categoria = db.categorias.find_one({'_id': ObjectId(pres_dict['categoria_id'])})
            if categoria:
                pres_dict['categoria_nombre'] = categoria.get('nombre')
                pres_dict['color'] = categoria.get('color')
                pres_dict['icono'] = categoria.get('icono')
        result.append(pres_dict)
    return result

def get_recordatorios(usuario_id=None):
    """Obtener recordatorios de pagos del usuario"""
    if db is None:
        return []
    query = {'estado': 'pendiente'}
    if usuario_id:
        query['usuario_id'] = usuario_id
    recordatorios = list(db.recordatorios.find(query).sort('fecha_vencimiento', 1))
    result = []
    for rec in recordatorios:
        rec_dict = convert_mongo_to_dict(rec)
        # Agregar información de tarjeta
        if rec_dict.get('tarjeta_id'):
            tarjeta = db.tarjetas.find_one({'_id': ObjectId(rec_dict['tarjeta_id'])})
            if tarjeta:
                rec_dict['tarjeta_nombre'] = tarjeta.get('nombre')
        # Agregar información de categoría
        if rec_dict.get('categoria_id'):
            categoria = db.categorias.find_one({'_id': ObjectId(rec_dict['categoria_id'])})
            if categoria:
                rec_dict['categoria_nombre'] = categoria.get('nombre')
        result.append(rec_dict)
    return result

def get_transactions(filtros=None, usuario_id=None):
    """Obtener transacciones con filtros del usuario"""
    if db is None:
        return []
    query = {}
    
    if usuario_id:
        query['usuario_id'] = usuario_id
    
    if filtros:
        if filtros.get('tipo'):
            query['tipo'] = filtros['tipo']
        if filtros.get('categoria_id'):
            query['categoria_id'] = filtros['categoria_id']
        if filtros.get('tarjeta_id'):
            query['tarjeta_id'] = filtros['tarjeta_id']
        if filtros.get('fecha_inicio'):
            query['fecha'] = {'$gte': filtros['fecha_inicio']}
        if filtros.get('fecha_fin'):
            if 'fecha' in query:
                query['fecha']['$lte'] = filtros['fecha_fin']
            else:
                query['fecha'] = {'$lte': filtros['fecha_fin']}
        if filtros.get('descripcion'):
            query['descripcion'] = {'$regex': filtros['descripcion'], '$options': 'i'}
    
    transacciones = list(db.transacciones.find(query).sort([('fecha', -1), ('created_at', -1)]))
    result = []
    for trans in transacciones:
        trans_dict = convert_mongo_to_dict(trans)
        # Agregar información de categoría
        if trans_dict.get('categoria_id'):
            categoria = db.categorias.find_one({'_id': ObjectId(trans_dict['categoria_id'])})
            if categoria:
                trans_dict['categoria_nombre'] = categoria.get('nombre')
                trans_dict['color'] = categoria.get('color')
                trans_dict['icono'] = categoria.get('icono')
        # Agregar información de tarjeta
        if trans_dict.get('tarjeta_id'):
            tarjeta = db.tarjetas.find_one({'_id': ObjectId(trans_dict['tarjeta_id'])})
            if tarjeta:
                trans_dict['tarjeta_nombre'] = tarjeta.get('nombre')
                trans_dict['tarjeta_color'] = tarjeta.get('color')
                trans_dict['tarjeta_icono'] = tarjeta.get('icono')
        result.append(trans_dict)
    return result

def get_balance(usuario_id=None):
    """Obtener balance total del usuario"""
    if db is None:
        return {'ingresos': 0, 'gastos': 0, 'balance': 0, 'membresias_mensuales': 0, 'balance_credito': 0}
    
    match_query = {}
    if usuario_id:
        match_query['usuario_id'] = usuario_id
    
    # Total ingresos
    ingresos_match = {**match_query, 'tipo': 'ingreso'}
    ingresos_cursor = db.transacciones.aggregate([
        {'$match': ingresos_match},
        {'$group': {'_id': None, 'total': {'$sum': '$monto'}}}
    ])
    total_ingresos = next(ingresos_cursor, {}).get('total', 0) or 0
    
    # Total gastos
    gastos_match = {**match_query, 'tipo': 'gasto'}
    gastos_cursor = db.transacciones.aggregate([
        {'$match': gastos_match},
        {'$group': {'_id': None, 'total': {'$sum': '$monto'}}}
    ])
    total_gastos = next(gastos_cursor, {}).get('total', 0) or 0
    
    # Total membresías mensuales
    membresias_match = {**match_query, 'estado': 'activa'}
    membresias_cursor = db.membresias.aggregate([
        {'$match': membresias_match},
        {'$group': {'_id': None, 'total': {'$sum': '$monto_mensual'}}}
    ])
    total_membresias = next(membresias_cursor, {}).get('total', 0) or 0
    
    # Balance de tarjetas de crédito
    tarjetas_query = {'tipo': 'credito', 'activa': True}
    if usuario_id:
        tarjetas_query['usuario_id'] = usuario_id
    tarjetas_credito = db.tarjetas.find(tarjetas_query)
    balance_credito = 0
    for tarjeta in tarjetas_credito:
        limite = tarjeta.get('limite_credito', 0)
        gastos_tarjeta_query = {'tarjeta_id': str(tarjeta['_id']), 'tipo': 'gasto'}
        if usuario_id:
            gastos_tarjeta_query['usuario_id'] = usuario_id
        gastos_tarjeta = db.transacciones.aggregate([
            {'$match': gastos_tarjeta_query},
            {'$group': {'_id': None, 'total': {'$sum': '$monto'}}}
        ])
        gastos_total = next(gastos_tarjeta, {}).get('total', 0) or 0
        balance_credito += limite - gastos_total
    
    balance = total_ingresos - total_gastos
    
    return {
        'ingresos': total_ingresos,
        'gastos': total_gastos,
        'balance': balance,
        'membresias_mensuales': total_membresias,
        'balance_credito': balance_credito
    }

def get_dashboard_stats(usuario_id=None):
    """Obtener estadísticas del dashboard del usuario"""
    if db is None:
        return {'gastos_por_categoria': [], 'proximos_vencimientos': [], 'recordatorios_urgentes': []}
    
    # Gastos por categoría este mes
    mes_actual = datetime.now().strftime('%Y-%m')
    inicio_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    fin_mes = (datetime.now().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    fin_mes_str = fin_mes.strftime('%Y-%m-%d')
    
    gastos_match = {'tipo': 'gasto', 'fecha': {'$gte': inicio_mes, '$lte': fin_mes_str}}
    if usuario_id:
        gastos_match['usuario_id'] = usuario_id
    
    gastos_cursor = db.transacciones.aggregate([
        {'$match': gastos_match},
        {'$group': {'_id': '$categoria_id', 'total': {'$sum': '$monto'}}},
        {'$sort': {'total': -1}},
        {'$limit': 10}
    ])
    
    gastos_por_categoria = []
    for item in gastos_cursor:
        categoria_id = item.get('_id')
        if categoria_id:
            categoria = db.categorias.find_one({'_id': ObjectId(categoria_id)})
            if categoria and categoria.get('tipo') == 'gasto' and categoria.get('activa'):
                gastos_por_categoria.append({
                    'nombre': categoria.get('nombre'),
                    'color': categoria.get('color'),
                    'icono': categoria.get('icono'),
                    'total': item.get('total', 0)
                })
    
    # Próximos vencimientos de tarjetas
    tarjetas_query = {'tipo': 'credito', 'activa': True}
    if usuario_id:
        tarjetas_query['usuario_id'] = usuario_id
    proximos_vencimientos = list(db.tarjetas.find(tarjetas_query).sort('fecha_vencimiento', 1).limit(5))
    proximos_vencimientos = convert_list_to_dicts(proximos_vencimientos)
    
    # Recordatorios urgentes (próximos 7 días)
    fecha_limite = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    recordatorios_query = {'estado': 'pendiente', 'fecha_vencimiento': {'$lte': fecha_limite}}
    if usuario_id:
        recordatorios_query['usuario_id'] = usuario_id
    recordatorios_urgentes = list(db.recordatorios.find(recordatorios_query).sort('fecha_vencimiento', 1).limit(5))
    recordatorios_urgentes = convert_list_to_dicts(recordatorios_urgentes)
    
    return {
        'gastos_por_categoria': gastos_por_categoria,
        'proximos_vencimientos': proximos_vencimientos,
        'recordatorios_urgentes': recordatorios_urgentes
    }

def get_categories(usuario_id=None):
    """Obtener todas las categorías del usuario"""
    if db is None:
        return []
    query = {}
    if usuario_id:
        query['usuario_id'] = usuario_id
    categorias = list(db.categorias.find(query).sort('nombre', 1))
    return convert_list_to_dicts(categorias)

def create_chart(transactions, chart_type='gastos_por_categoria'):
    """Crear gráficas"""
    if not transactions:
        return None
    
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    if chart_type == 'gastos_por_categoria':
        # Agrupar gastos por categoría
        gastos_por_cat = {}
        for t in transactions:
            if t['tipo'] == 'gasto':
                cat = t['categoria_nombre'] or 'Sin categoría'
                gastos_por_cat[cat] = gastos_por_cat.get(cat, 0) + t['monto']
        
        if gastos_por_cat:
            categorias = list(gastos_por_cat.keys())
            montos = list(gastos_por_cat.values())
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(categorias)))
            ax.pie(montos, labels=categorias, autopct='%1.1f%%', colors=colors)
            ax.set_title('Gastos por Categoría', fontsize=16, fontweight='bold')
    
    elif chart_type == 'balance_mensual':
        # Balance de los últimos 6 meses
        meses = []
        balances = []
        
        for i in range(6):
            fecha = datetime.now() - timedelta(days=30*i)
            mes = fecha.strftime('%Y-%m')
            meses.insert(0, fecha.strftime('%B %Y'))
            
            # Calcular balance del mes usando MongoDB
            if db is not None:
                inicio_mes = fecha.replace(day=1).strftime('%Y-%m-%d')
                fin_mes = (fecha.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                fin_mes_str = fin_mes.strftime('%Y-%m-%d')
                
                balance_cursor = db.transacciones.aggregate([
                    {'$match': {'fecha': {'$gte': inicio_mes, '$lte': fin_mes_str}}},
                    {'$group': {
                        '_id': None,
                        'balance': {
                            '$sum': {
                                '$cond': [
                                    {'$eq': ['$tipo', 'ingreso']},
                                    '$monto',
                                    {'$multiply': ['$monto', -1]}
                                ]
                            }
                        }
                    }}
                ])
                balance_result = next(balance_cursor, {})
                balance_mes = balance_result.get('balance', 0) or 0
            else:
                balance_mes = 0
            balances.insert(0, balance_mes)
        
        ax.bar(meses, balances, color=['#4CAF50' if b >= 0 else '#FF5722' for b in balances])
        ax.set_title('Balance Mensual', fontsize=16, fontweight='bold')
        ax.set_ylabel('Balance ($)')
        ax.tick_params(axis='x', rotation=45)
    
    # Convertir gráfica a base64
    img = StringIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()
    
    return img_base64

# Inicializar la base de datos cuando se importe el módulo
init_db()

# Templates HTML para Términos y Condiciones y Privacidad
TERMINOS_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Términos y Condiciones - Finanzas Gatunas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #667eea; margin-bottom: 30px; }
        h2 { color: #667eea; margin-top: 30px; margin-bottom: 15px; font-size: 1.5rem; }
        h3 { color: #555; margin-top: 20px; margin-bottom: 10px; }
        p { margin-bottom: 15px; line-height: 1.6; color: #333; }
        ul { margin-left: 30px; margin-bottom: 15px; }
        li { margin-bottom: 8px; line-height: 1.6; }
        a { color: #667eea; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e1e5e9; text-align: center; }
        .btn-back { display: inline-block; background: #667eea; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin-top: 20px; }
        .btn-back:hover { background: #5a6fd8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐱 TÉRMINOS Y CONDICIONES DE USO DE "FINANZAS GATUNAS"</h1>
        
        <p><strong>Última actualización:</strong> 4 de noviembre de 2025</p>
        
        <h2>1. Objeto del servicio</h2>
        <p>El presente documento establece los términos bajo los cuales <strong>Levi Eduardo Villarreal Argueta</strong> (en adelante, "el Proveedor"), con domicilio en <strong>Circuito Merlot 2081, México</strong>, pone a disposición del usuario (en adelante, "el Usuario") el acceso y uso de la aplicación web denominada <strong>"Finanzas Gatunas"</strong> (en adelante, "la Plataforma"), destinada a la <strong>gestión y registro de gastos personales y domésticos</strong>.</p>
        <p>El uso de la Plataforma implica la aceptación plena y sin reservas de los presentes Términos y Condiciones.</p>
        
        <h2>2. Cuentas de usuario y registro</h2>
        <p>Para acceder a algunas funciones, el Usuario podrá crear una cuenta, proporcionando datos verídicos y actualizados. El Usuario es responsable de mantener la confidencialidad de su contraseña y de todas las actividades realizadas desde su cuenta.</p>
        <p>El Proveedor no será responsable de accesos no autorizados derivados de negligencia del Usuario.</p>
        
        <h2>3. Uso del servicio</h2>
        <p>La Plataforma tiene como finalidad permitir al Usuario registrar, consultar y analizar sus gastos. El servicio puede incluir actualizaciones, mejoras y nuevas funciones.</p>
        <p>El Usuario se compromete a usar la Plataforma de forma lícita y conforme a la moral, las buenas costumbres y las leyes aplicables en México.</p>
        
        <h2>4. Modelo de monetización y pagos</h2>
        <p>Actualmente el servicio es <strong>gratuito</strong>. En el futuro podrá implementarse un modelo de <strong>suscripción mensual o anual</strong>, con acceso a funciones avanzadas. En caso de hacerlo, se informará oportunamente al Usuario antes de realizar cualquier cobro.</p>
        <p>No se ofrecerán reembolsos por pagos efectuados, salvo disposición legal en contrario.</p>
        
        <h2>5. Propiedad intelectual</h2>
        <p>Todos los derechos de propiedad intelectual sobre el software, logotipos, diseños, código fuente y demás elementos de la Plataforma son propiedad exclusiva de <strong>Levi Eduardo Villarreal Argueta</strong>, salvo contenido generado por los Usuarios.</p>
        <p>El Usuario conserva los derechos sobre la información que registre, pero otorga al Proveedor una licencia no exclusiva para usarla de forma agregada o anonimizada con fines estadísticos o de mejora del servicio.</p>
        
        <h2>6. Usos prohibidos</h2>
        <p>El Usuario se compromete a <strong>no realizar las siguientes acciones</strong>:</p>
        <ul>
            <li>a) Usar la Plataforma con fines ilícitos o fraudulentos.</li>
            <li>b) Introducir virus, malware o cualquier código dañino.</li>
            <li>c) Intentar obtener acceso no autorizado a cuentas, servidores o bases de datos.</li>
            <li>d) Realizar ingeniería inversa, descompilación o extracción del código fuente.</li>
            <li>e) Compartir credenciales con terceros sin autorización.</li>
            <li>f) Utilizar la Plataforma para enviar spam o recopilar información de otros usuarios.</li>
        </ul>
        <p>El incumplimiento podrá derivar en la suspensión o cancelación inmediata de la cuenta, sin perjuicio de las acciones legales correspondientes.</p>
        
        <h2>7. Limitación de responsabilidad</h2>
        <p>El Proveedor no garantiza la disponibilidad continua del servicio ni la ausencia de errores o fallos técnicos.</p>
        <p>En ningún caso será responsable de daños directos, indirectos, incidentales o consecuenciales derivados del uso o imposibilidad de uso de la Plataforma.</p>
        <p>El Usuario acepta que el servicio se ofrece "tal cual" y bajo su propio riesgo.</p>
        
        <h2>8. Modificaciones al servicio y a los términos</h2>
        <p>El Proveedor podrá modificar, actualizar o suspender temporalmente la Plataforma, así como modificar estos Términos y Condiciones.</p>
        <p>Las modificaciones serán notificadas a través de la propia Plataforma o por correo electrónico. El uso posterior de la Plataforma constituirá aceptación de dichas modificaciones.</p>
        
        <h2>9. Legislación aplicable y jurisdicción</h2>
        <p>Estos Términos se rigen por las leyes federales de los Estados Unidos Mexicanos.</p>
        <p>Para la interpretación y cumplimiento, las partes se someten a la <strong>jurisdicción de los tribunales competentes de la ciudad de Querétaro, México</strong>, renunciando a cualquier otro fuero que pudiera corresponderles.</p>
        
        <div class="footer">
            <h3>Contacto</h3>
            <p>Para cualquier duda sobre estos Términos y Condiciones, puede contactarnos en:</p>
            <p>📧 <a href="mailto:levi.eduardo2024@gmail.com">levi.eduardo2024@gmail.com</a></p>
            <a href="/register" class="btn-back">← Volver al Registro</a>
        </div>
    </div>
</body>
</html>
"""

PRIVACIDAD_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aviso de Privacidad - Finanzas Gatunas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #667eea; margin-bottom: 30px; }
        h2 { color: #667eea; margin-top: 30px; margin-bottom: 15px; font-size: 1.5rem; }
        h3 { color: #555; margin-top: 20px; margin-bottom: 10px; }
        p { margin-bottom: 15px; line-height: 1.6; color: #333; }
        ul { margin-left: 30px; margin-bottom: 15px; }
        li { margin-bottom: 8px; line-height: 1.6; }
        a { color: #667eea; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e1e5e9; text-align: center; }
        .btn-back { display: inline-block; background: #667eea; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin-top: 20px; }
        .btn-back:hover { background: #5a6fd8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐱 AVISO DE PRIVACIDAD INTEGRAL DE "FINANZAS GATUNAS"</h1>
        
        <p><strong>Última actualización:</strong> 4 de noviembre de 2025</p>
        
        <p>De conformidad con la <strong>Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP)</strong> y su Reglamento, se emite el presente Aviso de Privacidad.</p>
        
        <h2>1. Identidad y domicilio del responsable</h2>
        <p>El responsable del tratamiento de sus datos personales es <strong>Levi Eduardo Villarreal Argueta</strong>, con domicilio en <strong>Circuito Merlot 2081, México</strong>, y correo electrónico de contacto <a href="mailto:levi.eduardo2024@gmail.com">levi.eduardo2024@gmail.com</a>.</p>
        
        <h2>2. Datos personales recabados</h2>
        <p>Para el funcionamiento de la aplicación <strong>"Finanzas Gatunas"</strong>, se recaban los siguientes datos personales:</p>
        <ul>
            <li>Nombre (si el usuario lo proporciona).</li>
            <li>Correo electrónico.</li>
            <li>Información de gastos personales o domésticos ingresada voluntariamente.</li>
            <li>Dirección IP y cookies de sesión (para fines técnicos y analíticos).</li>
        </ul>
        <p>No se solicitan datos sensibles como información médica, ideológica o biométrica.</p>
        
        <h2>3. Finalidades del tratamiento</h2>
        <p>Los datos personales serán tratados para las siguientes <strong>finalidades primarias</strong>:</p>
        <ul>
            <li>a) Crear y administrar la cuenta del usuario.</li>
            <li>b) Permitir el registro, almacenamiento y visualización de gastos personales.</li>
            <li>c) Mejorar la funcionalidad y seguridad de la Plataforma.</li>
            <li>d) Proporcionar soporte técnico y atención al usuario.</li>
        </ul>
        <p>Y para las siguientes <strong>finalidades secundarias</strong>:</p>
        <ul>
            <li>a) Realizar análisis estadísticos anónimos de uso para optimizar el servicio.</li>
            <li>b) Desarrollar nuevas funcionalidades o productos relacionados.</li>
        </ul>
        <p>El usuario podrá <strong>manifestar su negativa</strong> para que sus datos sean tratados con estas finalidades secundarias enviando un correo a <a href="mailto:levi.eduardo2024@gmail.com">levi.eduardo2024@gmail.com</a>.</p>
        
        <h2>4. Transferencias de datos personales</h2>
        <p>Actualmente <strong>no se realizan transferencias de datos personales</strong> a terceros.</p>
        <p>En caso de que en el futuro se compartan datos con terceros (por ejemplo, procesadores de pago, servicios de correo o análisis), se notificará al usuario y se solicitará su consentimiento expreso, salvo aquellas transferencias permitidas por la Ley.</p>
        
        <h2>5. Medidas de seguridad</h2>
        <p>El responsable implementa medidas de seguridad administrativas, técnicas y físicas razonables para proteger los datos personales contra daño, pérdida, alteración, destrucción o acceso no autorizado.</p>
        
        <h2>6. Derechos ARCO (Acceso, Rectificación, Cancelación y Oposición)</h2>
        <p>Usted tiene derecho a acceder, rectificar, cancelar u oponerse al tratamiento de sus datos personales.</p>
        <p>Para ejercer estos derechos, deberá enviar una solicitud al correo <a href="mailto:levi.eduardo2024@gmail.com">levi.eduardo2024@gmail.com</a>, indicando:</p>
        <ul>
            <li>a) Nombre completo y medio para comunicarle la respuesta.</li>
            <li>b) Documentos que acrediten su identidad.</li>
            <li>c) Descripción clara del derecho que desea ejercer y los datos correspondientes.</li>
        </ul>
        <p>El responsable responderá su solicitud en un plazo máximo de <strong>20 días hábiles</strong> y, de resultar procedente, se hará efectiva dentro de los <strong>15 días hábiles</strong> siguientes.</p>
        
        <h2>7. Revocación del consentimiento</h2>
        <p>Usted puede revocar su consentimiento para el tratamiento de sus datos en cualquier momento, enviando su solicitud al correo antes indicado. Sin embargo, la revocación podría implicar la imposibilidad de seguir utilizando la Plataforma.</p>
        
        <h2>8. Uso de cookies y tecnologías similares</h2>
        <p>La Plataforma puede utilizar cookies y herramientas analíticas para mejorar la experiencia del usuario y obtener información estadística. El usuario puede desactivar el uso de cookies desde la configuración de su navegador.</p>
        
        <h2>9. Cambios al aviso de privacidad</h2>
        <p>El presente Aviso puede modificarse o actualizarse en cualquier momento. Las modificaciones estarán disponibles dentro de la propia aplicación web y se le notificará al usuario por los medios de contacto registrados.</p>
        
        <h2>10. Consentimiento del titular</h2>
        <p>Al utilizar la Plataforma o proporcionar sus datos personales, el usuario <strong>acepta</strong> el tratamiento de los mismos conforme a los términos de este Aviso de Privacidad.</p>
        
        <div class="footer">
            <h3>Contacto del responsable:</h3>
            <p>📧 <a href="mailto:levi.eduardo2024@gmail.com">levi.eduardo2024@gmail.com</a></p>
            <p>📍 <strong>Circuito Merlot 2081, México</strong></p>
            <a href="/register" class="btn-back">← Volver al Registro</a>
        </div>
    </div>
</body>
</html>
"""

# Templates HTML para autenticación
AUTH_TEMPLATES = {
    'login': """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar Sesión - Finanzas Gatunas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .auth-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .auth-header h1 {
            color: #667eea;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .auth-header p {
            color: #666;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-error {
            background: #ffeaea;
            color: #d32f2f;
            border-left: 4px solid #d32f2f;
        }
        .alert-success {
            background: #e8f5e8;
            color: #2e7d32;
            border-left: 4px solid #2e7d32;
        }
        .auth-links {
            text-align: center;
            margin-top: 20px;
        }
        .auth-links a {
            color: #667eea;
            text-decoration: none;
        }
        .auth-links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <h1>🐱 Finanzas Gatunas</h1>
            <p>Iniciar Sesión</p>
        </div>
        
        {% if error %}
        <div class="alert alert-error">{{ error }}</div>
        {% endif %}
        
        {% if mensaje %}
        <div class="alert alert-success">{{ mensaje }}</div>
        {% endif %}
        
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Contraseña</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">Iniciar Sesión</button>
        </form>
        
        <div class="auth-links">
            <p>¿No tienes cuenta? <a href="/register">Regístrate aquí</a></p>
        </div>
    </div>
</body>
</html>
""",
    'register': """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro - Finanzas Gatunas</title>
    <script>
        // Prellenar email si viene en la URL
        window.onload = function() {
            const emailInput = document.getElementById('email');
            const emailPrellenado = '{{ email_prellenado }}';
            if (emailPrellenado && emailInput) {
                emailInput.value = emailPrellenado;
            }
        }
    </script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .auth-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .auth-header h1 {
            color: #667eea;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .auth-header p {
            color: #666;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-error {
            background: #ffeaea;
            color: #d32f2f;
            border-left: 4px solid #d32f2f;
        }
        .auth-links {
            text-align: center;
            margin-top: 20px;
        }
        .auth-links a {
            color: #667eea;
            text-decoration: none;
        }
        .auth-links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <h1>🐱 Finanzas Gatunas</h1>
            <p>Crear Cuenta</p>
        </div>
        
        {% if error %}
        <div class="alert alert-error">{{ error }}</div>
        {% endif %}
        
        {% if mensaje %}
        <div class="alert alert-success">{{ mensaje }}</div>
        {% endif %}
        
        {% if invitacion_id %}
        <div class="alert alert-success" style="background: #e3f2fd; color: #1976d2; border-left: 4px solid #1976d2;">
            <i class="fas fa-info-circle"></i> Has sido invitado a compartir finanzas. Crea tu cuenta para aceptar la invitación.
        </div>
        {% endif %}
        
        <form method="POST" action="/register">
            {% if invitacion_id %}
            <input type="hidden" name="invitacion_id" value="{{ invitacion_id }}">
            {% endif %}
            
            <div class="form-group">
                <label for="nombre">Nombre (opcional)</label>
                <input type="text" id="nombre" name="nombre" placeholder="Tu nombre">
            </div>
            
            <div class="form-group">
                <label for="email">Email *</label>
                <input type="email" id="email" name="email" value="{{ email_prellenado }}" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Contraseña *</label>
                <input type="password" id="password" name="password" required minlength="6">
                <small style="color: #666; font-size: 12px;">Mínimo 6 caracteres</small>
            </div>
            
            <div class="form-group" style="margin-top: 20px;">
                <label style="display: flex; align-items: flex-start; cursor: pointer;">
                    <input type="checkbox" id="acepta_terminos" name="acepta_terminos" required style="margin-right: 10px; margin-top: 4px; width: auto;">
                    <span style="font-size: 14px;">
                        Acepto los <a href="/terminos" target="_blank" style="color: #667eea; text-decoration: underline;">Términos y Condiciones</a> 
                        y el <a href="/privacidad" target="_blank" style="color: #667eea; text-decoration: underline;">Aviso de Privacidad</a> *
                    </span>
                </label>
            </div>
            
            <button type="submit" class="btn">Registrarse</button>
        </form>
        
        <div class="auth-links">
            <p>¿Ya tienes cuenta? <a href="/login">Inicia sesión aquí</a></p>
        </div>
    </div>
</body>
</html>
""",
    'verify': """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verificar Email - Finanzas Gatunas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .auth-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .auth-header h1 {
            color: #667eea;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        .auth-header p {
            color: #666;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            text-align: center;
            letter-spacing: 8px;
            font-size: 24px;
            font-weight: bold;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
            margin-bottom: 10px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn-secondary {
            background: #9e9e9e;
        }
        .btn-secondary:hover {
            background: #757575;
        }
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-error {
            background: #ffeaea;
            color: #d32f2f;
            border-left: 4px solid #d32f2f;
        }
        .alert-success {
            background: #e8f5e8;
            color: #2e7d32;
            border-left: 4px solid #2e7d32;
        }
        .code-info {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <h1>🐱 Finanzas Gatunas</h1>
            <p>Verificar Email</p>
        </div>
        
        {% if error %}
        <div class="alert alert-error">{{ error }}</div>
        {% endif %}
        
        {% if mensaje %}
        <div class="alert alert-success">{{ mensaje }}</div>
        {% endif %}
        
        <div class="code-info">
            <p>Ingresa el código de verificación enviado a:</p>
            <p style="font-weight: bold; color: #667eea;">{{ email }}</p>
        </div>
        
        <form method="POST" action="/verify_email">
            <div class="form-group">
                <label for="codigo">Código de Verificación</label>
                <input type="text" id="codigo" name="codigo" required autofocus maxlength="6" pattern="[0-9]{6}">
            </div>
            
            <button type="submit" class="btn">Verificar</button>
        </form>
        
        <form method="POST" action="/resend_code">
            <button type="submit" class="btn btn-secondary">Reenviar Código</button>
        </form>
    </div>
</body>
</html>
"""
}

# HTML template principal
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>�� Finanzas Gatunas - Gestor Completo de Finanzas</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
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
            overflow-x: hidden;
        }
        
        .app-container {
            display: flex;
            min-height: 100vh;
        }
        
        .sidebar {
            width: 280px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            padding: 30px 20px;
            position: fixed;
            left: 0;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            box-shadow: 5px 0 25px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        
        .main-content {
            flex: 1;
            margin-left: 280px;
            padding: 20px;
            overflow-y: auto;
        }
        
        .sidebar-header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .sidebar-header h2 {
            color: #667eea;
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .sidebar-header p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .nav-menu {
            list-style: none;
        }
        
        .nav-item {
            margin-bottom: 10px;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            color: #555;
            text-decoration: none;
            border-radius: 12px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .nav-link:hover {
            background: #f8f9fa;
            color: #667eea;
            transform: translateX(5px);
        }
        
        .nav-link.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .nav-link i {
            margin-right: 15px;
            font-size: 1.2rem;
            width: 20px;
            text-align: center;
        }
        
        .section {
            display: none;
            animation: fadeIn 0.5s ease-in;
        }
        
        .section.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card.ingresos {
            border-left: 5px solid #4CAF50;
        }
        
        .stat-card.gastos {
            border-left: 5px solid #FF5722;
        }
        
        .stat-card.balance {
            border-left: 5px solid #2196F3;
        }
        
        .stat-card.membresias {
            border-left: 5px solid #9C27B0;
        }
        
        .stat-card.credito {
            border-left: 5px solid #FF9800;
        }
        
        .stat-card h3 {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #666;
        }
        
        .stat-card .amount {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-card.ingresos .amount {
            color: #4CAF50;
        }
        
        .stat-card.gastos .amount {
            color: #FF5722;
        }
        
        .stat-card.balance .amount {
            color: #2196F3;
        }
        
        .stat-card.membresias .amount {
            color: #9C27B0;
        }
        
        .stat-card.credito .amount {
            color: #FF9800;
        }
        
        .section-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .section-card h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
        }
        
        .section-card h3 i {
            margin-right: 10px;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #4CAF50;
            color: white;
        }
        
        .btn-danger {
            background: #FF5722;
            color: white;
        }
        
        .btn-warning {
            background: #FF9800;
            color: white;
        }
        
        .btn-info {
            background: #00BCD4;
            color: white;
        }
        
        .filter-total {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            border-left: 5px solid #667eea;
        }
        
        .filter-total h4 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .filter-total .amount {
            font-size: 1.8rem;
            font-weight: bold;
            color: #333;
        }
        
        .transactions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .transactions-table th,
        .transactions-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e1e5e9;
        }
        
        .transactions-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
        }
        
        .transactions-table tr:hover {
            background: #f8f9fa;
        }
        
        .transaction-type {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .transaction-type.ingreso {
            background: #e8f5e8;
            color: #4CAF50;
        }
        
        .transaction-type.gasto {
            background: #ffeaea;
            color: #FF5722;
        }
        
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .chart-controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        
        .empty-state i {
            font-size: 4rem;
            margin-bottom: 20px;
            color: #ddd;
        }
        
        .empty-state h4 {
            margin-bottom: 10px;
            color: #999;
        }
        
        .export-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .dashboard-widgets {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .widget {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .widget h4 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        
        .widget-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .widget-item:last-child {
            border-bottom: none;
        }
        
        .widget-item .label {
            color: #666;
        }
        
        .widget-item .value {
            font-weight: 600;
            color: #333;
        }
        
        .mobile-menu-toggle {
            display: none;
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1001;
            background: #667eea;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        @media (max-width: 1024px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .sidebar.open {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
            }
            
            .mobile-menu-toggle {
                display: block;
            }
        }
        
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .dashboard-widgets {
                grid-template-columns: 1fr;
            }
            
            .transactions-table {
                font-size: 14px;
            }
            
            .transactions-table th,
            .transactions-table td {
                padding: 10px 8px;
            }
            
            .chart-controls {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Botón de menú móvil -->
        <button class="mobile-menu-toggle" onclick="toggleSidebar()">
            <i class="fas fa-bars"></i>
        </button>
        
        <!-- Sidebar de navegación -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h2>🐱 Finanzas</h2>
                <p>Gestor Completo</p>
            </div>
            
            <ul class="nav-menu">
                <li class="nav-item">
                    <a href="#dashboard" class="nav-link active" onclick="showSection('dashboard')">
                        <i class="fas fa-tachometer-alt"></i>
                        Dashboard
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#transactions" class="nav-link" onclick="showSection('transactions')">
                        <i class="fas fa-plus-circle"></i>
                        Agregar
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#membresias" class="nav-link" onclick="showSection('membresias')">
                        <i class="fas fa-ticket-alt"></i>
                        Membresías
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#tarjetas" class="nav-link" onclick="showSection('tarjetas')">
                        <i class="fas fa-credit-card"></i>
                        Tarjetas
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#presupuestos" class="nav-link" onclick="showSection('presupuestos')">
                        <i class="fas fa-chart-pie"></i>
                        Presupuestos
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#filters" class="nav-link" onclick="showSection('filters')">
                        <i class="fas fa-filter"></i>
                        Filtros
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#list" class="nav-link" onclick="showSection('list')">
                        <i class="fas fa-list"></i>
                        Transacciones
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#recordatorios" class="nav-link" onclick="showSection('recordatorios')">
                        <i class="fas fa-bell"></i>
                        Recordatorios
                    </a>
                </li>
                <li class="nav-item">
                    <a href="#settings" class="nav-link" onclick="showSection('settings')">
                        <i class="fas fa-cog"></i>
                        Configuración
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/logout" class="nav-link">
                        <i class="fas fa-sign-out-alt"></i>
                        Cerrar Sesión
                    </a>
                </li>
            </ul>
        </div>
        
        <!-- Contenido principal -->
        <div class="main-content">
            <div class="header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1>🐱 Finanzas Gatunas</h1>
                        <p>Gestor completo de finanzas personales</p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="color: #667eea; font-weight: 600;">{{ usuario_actual.email }}</span>
                        <a href="/logout" style="background: #f44336; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-sign-out-alt"></i>
                            Cerrar Sesión
                        </a>
                    </div>
                </div>
            </div>
            
            <!-- Dashboard -->
            <div id="dashboard" class="section active">
                <div class="section-card">
                    <h3><i class="fas fa-tachometer-alt"></i> Resumen General</h3>
                    <div class="stats-grid">
                        <div class="stat-card ingresos">
                            <h3><i class="fas fa-arrow-up"></i> Total Ingresos</h3>
                            <div class="amount">${{ "%.2f"|format(balance.ingresos) }}</div>
                        </div>
                        <div class="stat-card gastos">
                            <h3><i class="fas fa-arrow-down"></i> Total Gastos</h3>
                            <div class="amount">${{ "%.2f"|format(balance.gastos) }}</div>
                        </div>
                        <div class="stat-card balance">
                            <h3><i class="fas fa-balance-scale"></i> Balance</h3>
                            <div class="amount">${{ "%.2f"|format(balance.balance) }}</div>
                        </div>
                        <div class="stat-card membresias">
                            <h3><i class="fas fa-ticket-alt"></i> Membresías Mensuales</h3>
                            <div class="amount">${{ "%.2f"|format(balance.membresias_mensuales) }}</div>
                        </div>
                        <div class="stat-card credito">
                            <h3><i class="fas fa-credit-card"></i> Crédito Disponible</h3>
                            <div class="amount">${{ "%.2f"|format(balance.balance_credito) }}</div>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-widgets">
                    <div class="widget">
                        <h4><i class="fas fa-chart-pie"></i> Gastos por Categoría (Este Mes)</h4>
                        {% for gasto in dashboard_stats.gastos_por_categoria %}
                        <div class="widget-item">
                            <span class="label">{{ gasto.icono }} {{ gasto.nombre }}</span>
                            <span class="value">${{ "%.2f"|format(gasto.total) }}</span>
                        </div>
                        {% endfor %}
                    </div>
                    
                    <div class="widget">
                        <h4><i class="fas fa-credit-card"></i> Próximos Vencimientos</h4>
                        {% for vencimiento in dashboard_stats.proximos_vencimientos %}
                        <div class="widget-item">
                            <span class="label">{{ vencimiento.nombre }}</span>
                            <span class="value">{{ vencimiento.fecha_vencimiento }}</span>
                        </div>
                        {% endfor %}
                    </div>
                    
                    <div class="widget">
                        <h4><i class="fas fa-bell"></i> Recordatorios Urgentes</h4>
                        {% for recordatorio in dashboard_stats.recordatorios_urgentes %}
                        <div class="widget-item">
                            <span class="label">{{ recordatorio.titulo }}</span>
                            <span class="value">${{ "%.2f"|format(recordatorio.monto) }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="section-card">
                    <h3><i class="fas fa-chart-pie"></i> Gráficas y Estadísticas</h3>
                    <div class="chart-controls">
                        <button onclick="changeChart('gastos_por_categoria')" class="btn btn-primary">
                            <i class="fas fa-chart-pie"></i> Gastos por Categoría
                        </button>
                        <button onclick="changeChart('balance_mensual')" class="btn btn-success">
                            <i class="fas fa-chart-line"></i> Balance Mensual
                        </button>
                    </div>
                    
                    <div class="chart-container">
                        {% if chart_data %}
                        <img src="data:image/png;base64,{{ chart_data }}" alt="Gráfica" id="chartImage">
                        {% else %}
                        <div class="empty-state">
                            <i class="fas fa-chart-bar"></i>
                            <h4>No hay datos para graficar</h4>
                            <p>Agrega algunas transacciones para ver las gráficas</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
            
            <!-- Agregar Transacciones -->
            <div id="transactions" class="section">
                <div class="section-card">
                    <h3><i class="fas fa-plus-circle"></i> Agregar Transacción</h3>
                    <form id="transactionForm" method="POST" action="/add_transaction">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="descripcion">Descripción *</label>
                                <input type="text" id="descripcion" name="descripcion" required>
                            </div>
                            <div class="form-group">
                                <label for="monto">Monto *</label>
                                <input type="number" id="monto" name="monto" step="0.01" min="0" required>
                            </div>
                            <div class="form-group">
                                <label for="tipo">Tipo *</label>
                                <select id="tipo" name="tipo" required>
                                    <option value="ingreso">Ingreso</option>
                                    <option value="gasto">Gasto</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="categoria_id">Categoría</label>
                                <select id="categoria_id" name="categoria_id">
                                    <option value="">Seleccionar categoría</option>
                                    {% for cat in categorias %}
                                        <option value="{{ cat.id }}" data-tipo="{{ cat.tipo }}">{{ cat.icono }} {{ cat.nombre }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="tarjeta_id">Método de Pago</label>
                                <select id="tarjeta_id" name="tarjeta_id">
                                    <option value="">Seleccionar método</option>
                                    {% for tar in tarjetas %}
                                        <option value="{{ tar.id }}">{{ tar.icono }} {{ tar.nombre }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="fecha">Fecha *</label>
                                <input type="date" id="fecha" name="fecha" value="{{ today }}" required>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="notas">Notas</label>
                                <textarea id="notas" name="notas" rows="1"></textarea>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Guardar Transacción
                        </button>
                    </form>
                </div>
            </div>
            
            <!-- Membresías -->
            <div id="membresias" class="section">
                <div class="section-card">
                    <h3><i class="fas fa-ticket-alt"></i> Membresías y Suscripciones</h3>
                    <div class="export-buttons">
                        <button class="btn btn-primary" onclick="showAddMembresiaForm()">
                            <i class="fas fa-plus"></i> Nueva Membresía
                        </button>
                    </div>
                    
                    <!-- Formulario para agregar membresía -->
                    <div id="addMembresiaForm" class="section-card" style="display: none; margin-top: 20px;">
                        <h4><i class="fas fa-plus"></i> Agregar Nueva Membresía</h4>
                        <form method="POST" action="/add_membresia">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="membresia_nombre">Nombre *</label>
                                    <input type="text" id="membresia_nombre" name="nombre" required>
                                </div>
                                <div class="form-group">
                                    <label for="membresia_plataforma">Plataforma *</label>
                                    <input type="text" id="membresia_plataforma" name="plataforma" required>
                                </div>
                                <div class="form-group">
                                    <label for="membresia_tipo">Tipo *</label>
                                    <select id="membresia_tipo" name="tipo" required>
                                        <option value="streaming">Streaming</option>
                                        <option value="musica">Música</option>
                                        <option value="fitness">Fitness</option>
                                        <option value="software">Software</option>
                                        <option value="otro">Otro</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="membresia_monto_mensual">Monto Mensual *</label>
                                    <input type="number" id="membresia_monto_mensual" name="monto_mensual" step="0.01" min="0" required>
                                </div>
                                <div class="form-group">
                                    <label for="membresia_monto_anual">Monto Anual</label>
                                    <input type="number" id="membresia_monto_anual" name="monto_anual" step="0.01" min="0">
                                </div>
                                <div class="form-group">
                                    <label for="membresia_tarjeta">Tarjeta</label>
                                    <select id="membresia_tarjeta" name="tarjeta_id">
                                        <option value="">Seleccionar tarjeta</option>
                                        {% for tar in tarjetas %}
                                            <option value="{{ tar.id }}">{{ tar.icono }} {{ tar.nombre }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="membresia_fecha_inicio">Fecha de Inicio *</label>
                                    <input type="date" id="membresia_fecha_inicio" name="fecha_inicio" required>
                                </div>
                                <div class="form-group">
                                    <label for="membresia_fecha_renovacion">Próxima Renovación</label>
                                    <input type="date" id="membresia_fecha_renovacion" name="fecha_renovacion">
                                </div>
                                <div class="form-group">
                                    <label for="membresia_notas">Notas</label>
                                    <textarea id="membresia_notas" name="notas" rows="1"></textarea>
                                </div>
                            </div>
                            <div class="form-row">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> Guardar Membresía
                                </button>
                                <button type="button" class="btn btn-warning" onclick="hideAddMembresiaForm()">
                                    <i class="fas fa-times"></i> Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    {% if membresias %}
                    <table class="transactions-table">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Plataforma</th>
                                <th>Tipo</th>
                                <th>Monto Mensual</th>
                                <th>Tarjeta</th>
                                <th>Próxima Renovación</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for m in membresias %}
                            <tr>
                                <td>{{ m.nombre }}</td>
                                <td>{{ m.plataforma }}</td>
                                <td>{{ m.tipo }}</td>
                                <td>${{ "%.2f"|format(m.monto_mensual) }}</td>
                                <td>
                                    {% if m.tarjeta_nombre %}
                                        <span style="color: {{ m.tarjeta_color }};">{{ m.tarjeta_icono }} {{ m.tarjeta_nombre }}</span>
                                    {% else %}
                                        <span style="color: #999;">No especificado</span>
                                    {% endif %}
                                </td>
                                <td>{{ m.fecha_renovacion }}</td>
                                <td>
                                    <span class="transaction-type {{ m.estado }}">
                                        {{ m.estado.title() }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="showEditMembresiaForm({{ m.id }}, '{{ m.nombre }}', '{{ m.plataforma }}', '{{ m.tipo }}', {{ m.monto_mensual }}, {{ m.monto_anual or 0 }}, {{ m.tarjeta_id or 'null' }}, '{{ m.fecha_inicio }}', '{{ m.fecha_renovacion or '' }}', '{{ m.notas or '' }}')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <a href="/delete_membresia/{{ m.id }}" class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="return confirm('¿Estás seguro de eliminar esta membresía?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <div class="empty-state">
                        <i class="fas fa-ticket-alt"></i>
                        <h4>No hay membresías</h4>
                        <p>Agrega tu primera membresía o suscripción</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Tarjetas -->
            <div id="tarjetas" class="section">
                <div class="section-card">
                    <h3><i class="fas fa-credit-card"></i> Tarjetas de Crédito y Débito</h3>
                    <div class="export-buttons">
                        <button class="btn btn-primary" onclick="showAddTarjetaForm()">
                            <i class="fas fa-plus"></i> Nueva Tarjeta
                        </button>
                    </div>
                    
                    <!-- Formulario para agregar tarjeta -->
                    <div id="addTarjetaForm" class="section-card" style="display: none; margin-top: 20px;">
                        <h4><i class="fas fa-plus"></i> Agregar Nueva Tarjeta</h4>
                        <form method="POST" action="/add_tarjeta">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="tarjeta_nombre">Nombre *</label>
                                    <input type="text" id="tarjeta_nombre" name="nombre" required>
                                </div>
                                <div class="form-group">
                                    <label for="tarjeta_tipo">Tipo *</label>
                                    <select id="tarjeta_tipo" name="tipo" required>
                                        <option value="efectivo">Efectivo</option>
                                        <option value="debito">Débito</option>
                                        <option value="credito">Crédito</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="tarjeta_banco">Banco</label>
                                    <input type="text" id="tarjeta_banco" name="banco" placeholder="Nombre del banco">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="tarjeta_limite">Límite de Crédito</label>
                                    <input type="number" id="tarjeta_limite" name="limite_credito" step="0.01" min="0" placeholder="Solo para tarjetas de crédito">
                                </div>
                                <div class="form-group">
                                    <label for="tarjeta_vencimiento">Fecha de Vencimiento</label>
                                    <input type="date" id="tarjeta_vencimiento" name="fecha_vencimiento">
                                </div>
                                <div class="form-group">
                                    <label for="tarjeta_color">Color</label>
                                    <input type="color" id="tarjeta_color" name="color" value="#667eea">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="tarjeta_icono">Icono</label>
                                    <select id="tarjeta_icono" name="icono">
                                        <option value="💳">💳 Tarjeta</option>
                                        <option value="💵">💵 Efectivo</option>
                                        <option value="🏦">🏦 Banco</option>
                                        <option value="💎">💎 Premium</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> Guardar Tarjeta
                                </button>
                                <button type="button" class="btn btn-warning" onclick="hideAddTarjetaForm()">
                                    <i class="fas fa-times"></i> Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    <!-- Formulario para editar tarjeta -->
                    <div id="editTarjetaForm" class="section-card" style="display: none; margin-top: 20px;">
                        <h4><i class="fas fa-edit"></i> Editar Tarjeta</h4>
                        <form method="POST" action="/edit_tarjeta/0" id="editTarjetaFormElement">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="edit_tarjeta_nombre">Nombre *</label>
                                    <input type="text" id="edit_tarjeta_nombre" name="nombre" required>
                                </div>
                                <div class="form-group">
                                    <label for="edit_tarjeta_tipo">Tipo *</label>
                                    <select id="edit_tarjeta_tipo" name="tipo" required>
                                        <option value="efectivo">Efectivo</option>
                                        <option value="debito">Débito</option>
                                        <option value="credito">Crédito</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="edit_tarjeta_banco">Banco</label>
                                    <input type="text" id="edit_tarjeta_banco" name="banco" placeholder="Nombre del banco">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="edit_tarjeta_limite">Límite de Crédito</label>
                                    <input type="number" id="edit_tarjeta_limite" name="limite_credito" step="0.01" min="0" placeholder="Solo para tarjetas de crédito">
                                </div>
                                <div class="form-group">
                                    <label for="edit_tarjeta_vencimiento">Fecha de Vencimiento</label>
                                    <input type="date" id="edit_tarjeta_vencimiento" name="fecha_vencimiento">
                                </div>
                                <div class="form-group">
                                    <label for="edit_tarjeta_color">Color</label>
                                    <input type="color" id="edit_tarjeta_color" name="color" value="#667eea">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="edit_tarjeta_icono">Icono</label>
                                    <select id="edit_tarjeta_icono" name="icono">
                                        <option value="💳">💳 Tarjeta</option>
                                        <option value="💵">💵 Efectivo</option>
                                        <option value="🏦">🏦 Banco</option>
                                        <option value="💎">💎 Premium</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> Actualizar Tarjeta
                                </button>
                                <button type="button" class="btn btn-warning" onclick="hideEditTarjetaForm()">
                                    <i class="fas fa-times"></i> Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    {% if tarjetas %}
                    <table class="transactions-table">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Tipo</th>
                                <th>Banco</th>
                                <th>Límite de Crédito</th>
                                <th>Vencimiento</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for tar in tarjetas %}
                            <tr>
                                <td>
                                    <span style="color: {{ tar.color }}; font-weight: bold;">{{ tar.icono }} {{ tar.nombre }}</span>
                                </td>
                                <td>
                                    <span class="transaction-type" style="background: {{ '#9C27B0' if tar.tipo == 'credito' else '#2196F3' if tar.tipo == 'debito' else '#4CAF50' }};">
                                        {{ tar.tipo.title() }}
                                    </span>
                                </td>
                                <td>{{ tar.banco or 'N/A' }}</td>
                                <td>
                                    {% if tar.tipo == 'credito' %}
                                        ${{ "%.2f"|format(tar.limite_credito) }}
                                    {% else %}
                                        N/A
                                    {% endif %}
                                </td>
                                <td>{{ tar.fecha_vencimiento or 'N/A' }}</td>
                                <td>
                                    <span class="transaction-type" style="background: {{ '#4CAF50' if tar.activa else '#FF5722' }};">
                                        {{ 'Activa' if tar.activa else 'Inactiva' }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="showEditTarjetaForm({{ tar.id }}, '{{ tar.nombre }}', '{{ tar.tipo }}', '{{ tar.banco or '' }}', {{ tar.limite_credito or 0 }}, '{{ tar.fecha_vencimiento or '' }}', '{{ tar.color }}', '{{ tar.icono }}')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <a href="/delete_tarjeta/{{ tar.id }}" class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="return confirm('¿Estás seguro de eliminar esta tarjeta?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <div class="empty-state">
                        <i class="fas fa-credit-card"></i>
                        <h4>No hay tarjetas</h4>
                        <p>Agrega tu primera tarjeta de crédito o débito</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Presupuestos -->
            <div id="presupuestos" class="section">
                <div class="section-card">
                    <h3><i class="fas fa-chart-pie"></i> Presupuestos Mensuales</h3>
                    <div class="export-buttons">
                        <button class="btn btn-primary" onclick="showAddPresupuestoForm()">
                            <i class="fas fa-plus"></i> Nuevo Presupuesto
                        </button>
                    </div>
                    
                    <!-- Formulario para agregar presupuesto -->
                    <div id="addPresupuestoForm" class="section-card" style="display: none; margin-top: 20px;">
                        <h4><i class="fas fa-plus"></i> Crear Nuevo Presupuesto</h4>
                        <form method="POST" action="/add_presupuesto">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="presupuesto_mes">Mes *</label>
                                    <select id="presupuesto_mes" name="mes" required>
                                        <option value="Enero">Enero</option>
                                        <option value="Febrero">Febrero</option>
                                        <option value="Marzo">Marzo</option>
                                        <option value="Abril">Abril</option>
                                        <option value="Mayo">Mayo</option>
                                        <option value="Junio">Junio</option>
                                        <option value="Julio">Julio</option>
                                        <option value="Agosto">Agosto</option>
                                        <option value="Septiembre">Septiembre</option>
                                        <option value="Octubre">Octubre</option>
                                        <option value="Noviembre">Noviembre</option>
                                        <option value="Diciembre">Diciembre</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="presupuesto_año">Año *</label>
                                    <input type="number" id="presupuesto_año" name="año" min="2024" max="2030" value="2024" required>
                                </div>
                                <div class="form-group">
                                    <label for="presupuesto_categoria">Categoría *</label>
                                    <select id="presupuesto_categoria" name="categoria_id" required>
                                        <option value="">Seleccionar categoría</option>
                                        {% for cat in categorias %}
                                            {% if cat.tipo == 'gasto' %}
                                                <option value="{{ cat.id }}">{{ cat.icono }} {{ cat.nombre }}</option>
                                            {% endif %}
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="presupuesto_monto">Monto Planificado *</label>
                                    <input type="number" id="presupuesto_monto" name="monto_planificado" step="0.01" min="0" required>
                                </div>
                            </div>
                            <div class="form-row">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> Crear Presupuesto
                                </button>
                                <button type="button" class="btn btn-warning" onclick="hideAddPresupuestoForm()">
                                    <i class="fas fa-times"></i> Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    {% if presupuestos %}
                    <table class="transactions-table">
                        <thead>
                            <tr>
                                <th>Mes/Año</th>
                                <th>Categoría</th>
                                <th>Planificado</th>
                                <th>Gastado</th>
                                <th>Restante</th>
                                <th>Porcentaje</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for p in presupuestos %}
                            {% set porcentaje = (p.monto_gastado / p.monto_planificado * 100) if p.monto_planificado > 0 else 0 %}
                            <tr>
                                <td>{{ p.mes }}/{{ p.año }}</td>
                                <td>
                                    <span style="color: {{ p.color }};">{{ p.icono }} {{ p.categoria_nombre }}</span>
                                </td>
                                <td>${{ "%.2f"|format(p.monto_planificado) }}</td>
                                <td>${{ "%.2f"|format(p.monto_gastado) }}</td>
                                <td>${{ "%.2f"|format(p.monto_planificado - p.monto_gastado) }}</td>
                                <td>
                                    <span style="color: {{ '#FF5722' if porcentaje > 100 else '#4CAF50' if porcentaje < 80 else '#FF9800' }};">
                                        {{ "%.1f"|format(porcentaje) }}%
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <div class="empty-state">
                        <i class="fas fa-chart-pie"></i>
                        <h4>No hay presupuestos</h4>
                        <p>Crea tu primer presupuesto mensual</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Filtros y Búsqueda -->
            <div id="filters" class="section">
                <div class="section-card">
                    <h3><i class="fas fa-filter"></i> Filtros y Búsqueda</h3>
                    <form id="filterForm" method="GET">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="filter_tipo">Tipo</label>
                                <select id="filter_tipo" name="filter_tipo">
                                    <option value="">Todos</option>
                                    <option value="ingreso">Ingresos</option>
                                    <option value="gasto">Gastos</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="filter_categoria">Categoría</label>
                                <select id="filter_categoria" name="filter_categoria">
                                    <option value="">Todas</option>
                                    {% for cat in categorias %}
                                        <option value="{{ cat.id }}">{{ cat.icono }} {{ cat.nombre }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="filter_tarjeta">Tarjeta</label>
                                <select id="filter_tarjeta" name="filter_tarjeta">
                                    <option value="">Todas</option>
                                    {% for tar in tarjetas %}
                                        <option value="{{ tar.id }}">{{ tar.icono }} {{ tar.nombre }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="filter_fecha_inicio">Fecha Inicio</label>
                                <input type="date" id="filter_fecha_inicio" name="filter_fecha_inicio">
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="filter_fecha_fin">Fecha Fin</label>
                                <input type="date" id="filter_fecha_fin" name="filter_fecha_fin">
                            </div>
                            <div class="form-group">
                                <label for="filter_descripcion">Descripción</label>
                                <input type="text" id="filter_descripcion" name="filter_descripcion" placeholder="Buscar en descripciones...">
                            </div>
                            <div class="form-group" style="display: flex; align-items: end;">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-search"></i> Aplicar Filtros
                                </button>
                                <a href="/" class="btn btn-warning" style="margin-left: 10px;">
                                    <i class="fas fa-times"></i> Limpiar
                                </a>
                            </div>
                        </div>
                    </form>
                    
                    {% if filtros_aplicados %}
                    <div class="filter-total">
                        <h4>Total del Filtro Aplicado</h4>
                        <div class="amount">
                            {% if filtros_aplicados.tipo == 'ingreso' %}
                                Ingresos: ${{ "%.2f"|format(total_filtrado) }}
                            {% elif filtros_aplicados.tipo == 'gasto' %}
                                Gastos: ${{ "%.2f"|format(total_filtrado) }}
                            {% else %}
                                Balance: ${{ "%.2f"|format(total_filtrado) }}
                            {% endif %}
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Lista de Transacciones -->
            <div id="list" class="section">
                <div class="section-card">
                    <h3><i class="fas fa-list"></i> Transacciones</h3>
                    
                    <div class="export-buttons">
                        <a href="/export_csv" class="btn btn-success">
                            <i class="fas fa-download"></i> Exportar CSV
                        </a>
                        <a href="/export_json" class="btn btn-warning">
                            <i class="fas fa-code"></i> Exportar JSON
                        </a>
                    </div>
                    
                    {% if transacciones %}
                    <table class="transactions-table">
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>Descripción</th>
                                <th>Categoría</th>
                                <th>Método de Pago</th>
                                <th>Monto</th>
                                <th>Tipo</th>
                                <th>Notas</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for t in transacciones %}
                            <tr>
                                <td>{{ t.fecha }}</td>
                                <td>{{ t.descripcion }}</td>
                                <td>
                                    {% if t.categoria_nombre %}
                                        <span style="color: {{ t.color }};">{{ t.icono }} {{ t.categoria_nombre }}</span>
                                    {% else %}
                                        <span style="color: #999;">Sin categoría</span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if t.tarjeta_nombre %}
                                        <span style="color: {{ t.tarjeta_color }};">{{ t.tarjeta_icono }} {{ t.tarjeta_nombre }}</span>
                                    {% else %}
                                        <span style="color: #999;">No especificado</span>
                                    {% endif %}
                                </td>
                                <td style="font-weight: bold; color: {{ '#4CAF50' if t.tipo == 'ingreso' else '#FF5722' }};">
                                    ${{ "%.2f"|format(t.monto) }}
                                </td>
                                <td>
                                    <span class="transaction-type {{ t.tipo }}">
                                        {{ t.tipo.title() }}
                                    </span>
                                </td>
                                <td>{{ t.notas or '-' }}</td>
                                <td>
                                    <a href="/edit_transaction/{{ t.id }}" class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <a href="/delete_transaction/{{ t.id }}" class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" 
                                       onclick="return confirm('¿Estás seguro de eliminar esta transacción?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <h4>No hay transacciones</h4>
                        <p>Agrega tu primera transacción usando el formulario de arriba</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Recordatorios -->
            <div id="recordatorios" class="section">
                <div class="section-card">
                    <h3><i class="fas fa-bell"></i> Recordatorios de Pagos</h3>
                    <button onclick="showAddRecordatorioForm()" class="btn-primary">
                        <i class="fas fa-plus"></i> Agregar Recordatorio
                    </button>
                    
                    <div id="addRecordatorioForm" style="display: none; margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                        <form action="/add_recordatorio" method="POST">
                            <div class="form-group">
                                <label>Descripción *</label>
                                <input type="text" name="descripcion" required>
                            </div>
                            <div class="form-group">
                                <label>Monto *</label>
                                <input type="number" step="0.01" name="monto" required>
                            </div>
                            <div class="form-group">
                                <label>Fecha de Vencimiento *</label>
                                <input type="date" name="fecha_vencimiento" id="recordatorio_fecha" required>
                            </div>
                            <div class="form-group">
                                <label>Tarjeta</label>
                                <select name="tarjeta_id">
                                    <option value="">Seleccionar tarjeta</option>
                                    {% for tarjeta in tarjetas %}
                                    <option value="{{ tarjeta.id }}">{{ tarjeta.icono }} {{ tarjeta.nombre }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Categoría</label>
                                <select name="categoria_id">
                                    <option value="">Seleccionar categoría</option>
                                    {% for categoria in categorias %}
                                    {% if categoria.tipo == 'gasto' %}
                                    <option value="{{ categoria.id }}">{{ categoria.icono }} {{ categoria.nombre }}</option>
                                    {% endif %}
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Notas</label>
                                <textarea name="notas" rows="3"></textarea>
                            </div>
                            <button type="submit" class="btn-primary">Agregar</button>
                            <button type="button" onclick="hideAddRecordatorioForm()" class="btn-secondary">Cancelar</button>
                        </form>
                    </div>
                    
                    <div class="table-container">
                        <table class="transactions-table">
                            <thead>
                                <tr>
                                    <th>Descripción</th>
                                    <th>Monto</th>
                                    <th>Fecha Vencimiento</th>
                                    <th>Tarjeta</th>
                                    <th>Categoría</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% if recordatorios %}
                                {% for recordatorio in recordatorios %}
                                <tr>
                                    <td>{{ recordatorio.descripcion }}</td>
                                    <td>${{ "%.2f"|format(recordatorio.monto) }}</td>
                                    <td>{{ recordatorio.fecha_vencimiento }}</td>
                                    <td>{{ recordatorio.tarjeta_nombre or 'N/A' }}</td>
                                    <td>{{ recordatorio.categoria_nombre or 'N/A' }}</td>
                                    <td>
                                        <span class="transaction-type gasto">{{ recordatorio.estado }}</span>
                                    </td>
                                    <td>
                                        <a href="/completar_recordatorio/{{ recordatorio.id }}" class="btn-icon" title="Marcar como completado">
                                            <i class="fas fa-check"></i>
                                        </a>
                                        <a href="/edit_recordatorio/{{ recordatorio.id }}" class="btn-icon" title="Editar">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <a href="/delete_recordatorio/{{ recordatorio.id }}" class="btn-icon" title="Eliminar" onclick="return confirm('¿Estás seguro?')">
                                            <i class="fas fa-trash"></i>
                                        </a>
                                    </td>
                                </tr>
                                {% endfor %}
                                {% else %}
                                <tr>
                                    <td colspan="7" class="empty-state">
                                        <i class="fas fa-bell-slash"></i>
                                        <h4>No hay recordatorios</h4>
                                        <p>Agrega recordatorios para no olvidar tus pagos</p>
                                    </td>
                                </tr>
                                {% endif %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Configuración e Invitaciones -->
            <div id="settings" class="section">
                <div class="section-card">
                    <h3><i class="fas fa-cog"></i> Configuración</h3>
                    
                    <div style="margin-bottom: 30px;">
                        <h4 style="color: #667eea; margin-bottom: 15px;">
                            <i class="fas fa-user"></i> Usuario Actual
                        </h4>
                        <p><strong>Email:</strong> {{ usuario_actual.email }}</p>
                        <p><strong>Nombre:</strong> {{ usuario_actual.nombre or 'No especificado' }}</p>
                        <p><strong>Email Verificado:</strong> {% if usuario_actual.email_verificado %}✅ Sí{% else %}❌ No{% endif %}</p>
                    </div>
                    
                    <div style="margin-bottom: 30px;">
                        <h4 style="color: #667eea; margin-bottom: 15px;">
                            <i class="fas fa-user-plus"></i> Invitar Usuario
                        </h4>
                        <form action="/invite" method="POST" style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                            <div class="form-group">
                                <label>Email del Usuario a Invitar *</label>
                                <input type="email" name="email" required placeholder="usuario@ejemplo.com">
                            </div>
                            <div class="form-group">
                                <label>Permiso *</label>
                                <select name="permiso" required>
                                    <option value="ver">Solo Ver</option>
                                    <option value="editar">Ver y Editar</option>
                                </select>
                            </div>
                            <button type="submit" class="btn-primary">
                                <i class="fas fa-paper-plane"></i> Enviar Invitación
                            </button>
                        </form>
                    </div>
                    
                    {% if invitaciones_pendientes %}
                    <div style="margin-bottom: 30px;">
                        <h4 style="color: #667eea; margin-bottom: 15px;">
                            <i class="fas fa-clock"></i> Invitaciones Recibidas Pendientes
                        </h4>
                        <div class="table-container">
                            <table class="transactions-table">
                                <thead>
                                    <tr>
                                        <th>De</th>
                                        <th>Permiso</th>
                                        <th>Fecha</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for inv in invitaciones_pendientes %}
                                    <tr>
                                        <td>{{ inv.propietario_nombre or inv.propietario_email }}</td>
                                        <td>{{ 'Ver y Editar' if inv.permiso == 'editar' else 'Solo Ver' }}</td>
                                        <td>{{ inv.created_at.strftime('%Y-%m-%d') if inv.created_at else 'N/A' }}</td>
                                        <td>
                                            <a href="/accept_invitation?invitacion_id={{ inv.id }}" class="btn-icon" title="Aceptar" style="color: #4CAF50;">
                                                <i class="fas fa-check"></i>
                                            </a>
                                            <a href="/reject_invitation/{{ inv.id }}" class="btn-icon" title="Rechazar" style="color: #f44336;" onclick="return confirm('¿Rechazar esta invitación?')">
                                                <i class="fas fa-times"></i>
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if invitaciones_enviadas %}
                    <div style="margin-bottom: 30px;">
                        <h4 style="color: #667eea; margin-bottom: 15px;">
                            <i class="fas fa-paper-plane"></i> Invitaciones Enviadas
                        </h4>
                        <div class="table-container">
                            <table class="transactions-table">
                                <thead>
                                    <tr>
                                        <th>Para</th>
                                        <th>Permiso</th>
                                        <th>Estado</th>
                                        <th>Fecha</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for inv in invitaciones_enviadas %}
                                    <tr>
                                        <td>{{ inv.invitado_nombre or inv.invitado_email }}</td>
                                        <td>{{ 'Ver y Editar' if inv.permiso == 'editar' else 'Solo Ver' }}</td>
                                        <td>
                                            <span class="transaction-type {% if inv.estado == 'aceptada' %}ingreso{% else %}gasto{% endif %}">
                                                {{ inv.estado|title }}
                                            </span>
                                        </td>
                                        <td>{{ inv.created_at.strftime('%Y-%m-%d') if inv.created_at else 'N/A' }}</td>
                                        <td>
                                            {% if inv.estado == 'pendiente' %}
                                            <a href="/remove_invitation/{{ inv.id }}" class="btn-icon" title="Cancelar" style="color: #f44336;" onclick="return confirm('¿Cancelar esta invitación?')">
                                                <i class="fas fa-trash"></i>
                                            </a>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if invitaciones_aceptadas %}
                    <div style="margin-bottom: 30px;">
                        <h4 style="color: #667eea; margin-bottom: 15px;">
                            <i class="fas fa-users"></i> Finanzas Compartidas Conmigo
                        </h4>
                        <div class="table-container">
                            <table class="transactions-table">
                                <thead>
                                    <tr>
                                        <th>Propietario</th>
                                        <th>Permiso</th>
                                        <th>Fecha de Aceptación</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for inv in invitaciones_aceptadas %}
                                    <tr>
                                        <td>{{ inv.propietario_nombre or inv.propietario_email }}</td>
                                        <td>{{ 'Ver y Editar' if inv.permiso == 'editar' else 'Solo Ver' }}</td>
                                        <td>{{ inv.fecha_aceptacion.strftime('%Y-%m-%d') if inv.fecha_aceptacion else 'N/A' }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        <p style="color: #666; font-size: 14px; margin-top: 10px;">
                            <i class="fas fa-info-circle"></i> Puedes ver y editar las finanzas de estos usuarios según el permiso asignado.
                        </p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Navegación entre secciones
        function showSection(sectionId) {
            // Ocultar todas las secciones
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Mostrar la sección seleccionada
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            // Actualizar menú activo
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + sectionId) {
                    link.classList.add('active');
                }
            });
        }
        
        // Cambiar gráfica
        function changeChart(chartType) {
            window.location.href = '/?chart_type=' + chartType;
        }
        
        // Toggle sidebar en móvil
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            if (sidebar) {
                sidebar.classList.toggle('open');
            }
        }
        
        // ===== FUNCIONES PARA FORMULARIOS =====
        
        // Membresías
        function showAddMembresiaForm() {
            const form = document.getElementById('addMembresiaForm');
            if (form) {
                form.style.display = 'block';
                // Establecer fecha actual por defecto
                const today = new Date().toISOString().split('T')[0];
                const fechaInput = document.getElementById('membresia_fecha_inicio');
                if (fechaInput) {
                    fechaInput.value = today;
                }
            }
        }
        
        function hideAddMembresiaForm() {
            const form = document.getElementById('addMembresiaForm');
            if (form) {
                form.style.display = 'none';
            }
        }
        
        function showEditMembresiaForm(id, nombre, plataforma, tipo, monto_mensual, monto_anual, tarjeta_id, fecha_inicio, fecha_renovacion, notas) {
            // Por ahora redirigimos a la página principal con parámetros de edición
            // En una versión futura podríamos mostrar un modal o formulario de edición
            window.location.href = '/?edit_membresia_id=' + id;
        }
        
        // Tarjetas
        function showAddTarjetaForm() {
            const form = document.getElementById('addTarjetaForm');
            if (form) {
                form.style.display = 'block';
            }
        }
        
        function hideAddTarjetaForm() {
            const form = document.getElementById('addTarjetaForm');
            if (form) {
                form.style.display = 'none';
            }
        }
        
        function showEditTarjetaForm(id, nombre, tipo, banco, limite_credito, fecha_vencimiento, color, icono) {
            // Actualizar la acción del formulario con el ID correcto
            const formElement = document.getElementById('editTarjetaFormElement');
            if (formElement) {
                formElement.action = '/edit_tarjeta/' + id;
            }
            
            // Llenar los campos con los datos actuales
            const nombreInput = document.getElementById('edit_tarjeta_nombre');
            const tipoInput = document.getElementById('edit_tarjeta_tipo');
            const bancoInput = document.getElementById('edit_tarjeta_banco');
            const limiteInput = document.getElementById('edit_tarjeta_limite');
            const vencimientoInput = document.getElementById('edit_tarjeta_vencimiento');
            const colorInput = document.getElementById('edit_tarjeta_color');
            const iconoInput = document.getElementById('edit_tarjeta_icono');
            
            if (nombreInput) nombreInput.value = nombre || '';
            if (tipoInput) tipoInput.value = tipo || '';
            if (bancoInput) bancoInput.value = banco || '';
            if (limiteInput) limiteInput.value = limite_credito || 0;
            if (vencimientoInput) vencimientoInput.value = fecha_vencimiento || '';
            if (colorInput) colorInput.value = color || '#667eea';
            if (iconoInput) iconoInput.value = icono || '💳';
            
            // Mostrar el formulario
            const editForm = document.getElementById('editTarjetaForm');
            if (editForm) {
                editForm.style.display = 'block';
            }
            
            // Ocultar el formulario de agregar si está visible
            const addForm = document.getElementById('addTarjetaForm');
            if (addForm) {
                addForm.style.display = 'none';
            }
        }
        
        function hideEditTarjetaForm() {
            const form = document.getElementById('editTarjetaForm');
            if (form) {
                form.style.display = 'none';
            }
        }
        
        // Presupuestos
        function showAddPresupuestoForm() {
            const form = document.getElementById('addPresupuestoForm');
            if (form) {
                form.style.display = 'block';
                // Establecer mes y año actual por defecto
                const now = new Date();
                const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                const mesInput = document.getElementById('presupuesto_mes');
                const añoInput = document.getElementById('presupuesto_año');
                if (mesInput) mesInput.value = months[now.getMonth()];
                if (añoInput) añoInput.value = now.getFullYear();
            }
        }
        
        function hideAddPresupuestoForm() {
            const form = document.getElementById('addPresupuestoForm');
            if (form) {
                form.style.display = 'none';
            }
        }
        
        // Recordatorios
        function showAddRecordatorioForm() {
            const form = document.getElementById('addRecordatorioForm');
            if (form) {
                form.style.display = 'block';
                // Establecer fecha actual por defecto
                const today = new Date().toISOString().split('T')[0];
                const fechaInput = document.getElementById('recordatorio_fecha');
                if (fechaInput) {
                    fechaInput.value = today;
                }
            }
        }
        
        function hideAddRecordatorioForm() {
            const form = document.getElementById('addRecordatorioForm');
            if (form) {
                form.style.display = 'none';
            }
        }
        
        function showEditRecordatorioForm(id, titulo, descripcion, monto, fecha_vencimiento, tarjeta_id, categoria_id, prioridad) {
            // Por ahora redirigimos a la página principal con parámetros de edición
            window.location.href = '/?edit_recordatorio_id=' + id;
        }
        
        // Inicializar cuando el DOM esté completamente cargado
        document.addEventListener('DOMContentLoaded', function() {
            // Establecer fecha actual en formularios de transacciones
            const today = new Date().toISOString().split('T')[0];
            const fechaInput = document.getElementById('fecha');
            if (fechaInput) {
                fechaInput.value = today;
            }
            
            // Cambiar tipo de transacción - solo si el elemento existe
            const tipoSelect = document.getElementById('tipo');
            if (tipoSelect) {
                tipoSelect.addEventListener('change', function() {
                    const tipo = this.value;
                    const categoriaSelect = document.getElementById('categoria_id');
                    if (categoriaSelect) {
                        const options = categoriaSelect.options;
                        
                        // Limpiar selección actual
                        categoriaSelect.value = '';
                        
                        // Mostrar solo categorías del tipo seleccionado
                        for (let i = 0; i < options.length; i++) {
                            const option = options[i];
                            if (option.value === '') continue; // Saltar opción "Seleccionar categoría"
                            
                            const dataTipo = option.getAttribute('data-tipo');
                            if (dataTipo === tipo) {
                                option.style.display = '';
                            } else {
                                option.style.display = 'none';
                            }
                        }
                    }
                });
            }
            
            // Aplicar filtros automáticamente - solo si el formulario existe
            const filterForm = document.getElementById('filterForm');
            if (filterForm) {
                filterForm.addEventListener('submit', function() {
                    // Agregar parámetros de gráfica si existen
                    const urlParams = new URLSearchParams(window.location.search);
                    const chartType = urlParams.get('chart_type');
                    if (chartType) {
                        const input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = 'chart_type';
                        input.value = chartType;
                        this.appendChild(input);
                    }
                });
            }
            
            // Cerrar sidebar al hacer clic fuera en móvil
            document.addEventListener('click', function(event) {
                const sidebar = document.getElementById('sidebar');
                const mobileToggle = document.querySelector('.mobile-menu-toggle');
                
                if (window.innerWidth <= 1024 && sidebar && mobileToggle &&
                    !sidebar.contains(event.target) && 
                    !mobileToggle.contains(event.target)) {
                    sidebar.classList.remove('open');
                }
            });
            
            // Verificar si hay un parámetro de sección en la URL
            const urlParams = new URLSearchParams(window.location.search);
            const section = urlParams.get('section');
            if (section) {
                // Mostrar la sección especificada
                showSection(section);
                
                // Marcar el enlace activo
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === '#' + section) {
                        link.classList.add('active');
                    }
                });
            }
        });
    </script>
</body>
</html>
"""

# ===== RUTAS DE AUTENTICACIÓN =====

@app.route('/terminos')
def terminos():
    """Mostrar términos y condiciones"""
    return render_template_string(TERMINOS_TEMPLATE)

@app.route('/privacidad')
def privacidad():
    """Mostrar aviso de privacidad"""
    return render_template_string(PRIVACIDAD_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevo usuario"""
    if request.method == 'POST':
        if db is None:
            return jsonify({'error': 'Base de datos no disponible'}), 500
        
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        nombre = request.form.get('nombre', '').strip()
        invitacion_id = request.form.get('invitacion_id') or session.get('invitacion_pendiente')
        acepta_terminos = request.form.get('acepta_terminos') == 'on'
        
        # Validaciones
        if not email or not password:
            error_msg = 'Email y contraseña son requeridos'
            if invitacion_id:
                return redirect(f'/register?error={error_msg}&invitacion_id={invitacion_id}&email={email}')
            return redirect(f'/register?error={error_msg}')
        
        if len(password) < 6:
            error_msg = 'La contraseña debe tener al menos 6 caracteres'
            if invitacion_id:
                return redirect(f'/register?error={error_msg}&invitacion_id={invitacion_id}&email={email}')
            return redirect(f'/register?error={error_msg}')
        
        if not acepta_terminos:
            error_msg = 'Debes aceptar los términos y condiciones y el aviso de privacidad para registrarte'
            if invitacion_id:
                return redirect(f'/register?error={error_msg}&invitacion_id={invitacion_id}&email={email}')
            return redirect(f'/register?error={error_msg}')
        
        # Verificar si el usuario ya existe
        if db.usuarios.find_one({'email': email}):
            error_msg = 'Este email ya está registrado. Por favor inicia sesión.'
            if invitacion_id:
                return redirect(f'/login?error={error_msg}&invitacion_id={invitacion_id}')
            return redirect('/register?error=' + error_msg)
        
        # Crear usuario
        usuario = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'nombre': nombre or email.split('@')[0],
            'email_verificado': False,
            'acepta_terminos': True,
            'fecha_aceptacion_terminos': datetime.now(),
            'created_at': datetime.now()
        }
        
        resultado = db.usuarios.insert_one(usuario)
        usuario_id = str(resultado.inserted_id)
        
        # Si hay una invitación pendiente, actualizarla con el ID del usuario
        if invitacion_id:
            try:
                invitacion = db.invitaciones.find_one({'_id': ObjectId(invitacion_id)})
                if invitacion and invitacion.get('email_invitado', '').lower() == email.lower():
                    db.invitaciones.update_one(
                        {'_id': ObjectId(invitacion_id)},
                        {'$set': {'usuario_invitado_id': usuario_id}}
                    )
            except:
                pass
        
        # Generar y enviar código de verificación
        codigo = generar_codigo_verificacion()
        codigo_doc = {
            'usuario_id': usuario_id,
            'email': email,
            'codigo': codigo,
            'expiracion': datetime.now() + timedelta(minutes=15),
            'usado': False,
            'created_at': datetime.now()
        }
        db.codigos_verificacion.insert_one(codigo_doc)
        
        # Intentar enviar email (si no está configurado, mostrar código en consola)
        if app.config.get('MAIL_USERNAME'):
            enviar_codigo_verificacion(email, codigo)
            mensaje = 'Se ha enviado un código de verificación a tu email'
        else:
            print(f"[INFO] Código de verificación para {email}: {codigo}")
            mensaje = f'Código de verificación (modo desarrollo): {codigo}'
        
        # Guardar email en sesión para verificación
        session['email_pendiente'] = email
        session['usuario_id_pendiente'] = usuario_id
        if invitacion_id:
            session['invitacion_pendiente'] = invitacion_id
        
        return redirect(f'/verify_email?mensaje={mensaje}&invitacion_id={invitacion_id}' if invitacion_id else f'/verify_email?mensaje={mensaje}')
    
    # GET: Mostrar formulario de registro
    error = request.args.get('error', '')
    mensaje = request.args.get('mensaje', '')
    invitacion_id = request.args.get('invitacion_id', '')
    email_prellenado = request.args.get('email', '')
    
    # Guardar invitacion_id en sesión si viene por URL
    if invitacion_id:
        session['invitacion_pendiente'] = invitacion_id
    
    return render_template_string(AUTH_TEMPLATES['register'], error=error, mensaje=mensaje, invitacion_id=invitacion_id, email_prellenado=email_prellenado)

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    """Verificar email con código"""
    if request.method == 'POST':
        if db is None:
            return redirect('/verify_email?error=Base de datos no disponible')
        
        codigo = request.form.get('codigo', '').strip()
        email = session.get('email_pendiente')
        
        if not email:
            return redirect('/register?error=Sesión expirada, por favor regístrate de nuevo')
        
        # Buscar código válido
        codigo_doc = db.codigos_verificacion.find_one({
            'email': email,
            'codigo': codigo,
            'usado': False,
            'expiracion': {'$gt': datetime.now()}
        })
        
        if not codigo_doc:
            return redirect('/verify_email?error=Código inválido o expirado')
        
        # Marcar código como usado
        db.codigos_verificacion.update_one(
            {'_id': codigo_doc['_id']},
            {'$set': {'usado': True}}
        )
        
        # Verificar email del usuario
        usuario_id = session.get('usuario_id_pendiente')
        db.usuarios.update_one(
            {'_id': ObjectId(usuario_id)},
            {'$set': {'email_verificado': True}}
        )
        
        # Verificar si hay una invitación pendiente
        invitacion_id = session.get('invitacion_pendiente') or request.args.get('invitacion_id')
        
        # Limpiar sesión
        session.pop('email_pendiente', None)
        session.pop('usuario_id_pendiente', None)
        
        # Si hay invitación pendiente, redirigir a aceptarla después del login
        if invitacion_id:
            return redirect(f'/login?invitacion_id={invitacion_id}&mensaje=Email verificado. Inicia sesión para aceptar la invitación.')
        
        return redirect('/login?mensaje=Email verificado correctamente. Inicia sesión.')
    
    # GET: Mostrar formulario de verificación
    error = request.args.get('error', '')
    mensaje = request.args.get('mensaje', '')
    email = session.get('email_pendiente', '')
    return render_template_string(AUTH_TEMPLATES['verify'], error=error, mensaje=mensaje, email=email)

@app.route('/resend_code', methods=['POST'])
def resend_code():
    """Reenviar código de verificación"""
    if db is None:
        return redirect('/verify_email?error=Base de datos no disponible')
    
    email = session.get('email_pendiente')
    if not email:
        return redirect('/register?error=Sesión expirada')
    
    # Generar nuevo código
    codigo = generar_codigo_verificacion()
    usuario = db.usuarios.find_one({'email': email})
    
    if usuario:
        codigo_doc = {
            'usuario_id': str(usuario['_id']),
            'email': email,
            'codigo': codigo,
            'expiracion': datetime.now() + timedelta(minutes=15),
            'usado': False,
            'created_at': datetime.now()
        }
        db.codigos_verificacion.insert_one(codigo_doc)
        
        if app.config.get('MAIL_USERNAME'):
            enviar_codigo_verificacion(email, codigo)
            mensaje = 'Código reenviado a tu email'
        else:
            print(f"[INFO] Nuevo código para {email}: {codigo}")
            mensaje = f'Nuevo código (modo desarrollo): {codigo}'
        
        return redirect(f'/verify_email?mensaje={mensaje}')
    
    return redirect('/register?error=Usuario no encontrado')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Iniciar sesión"""
    if request.method == 'POST':
        if db is None:
            return redirect('/login?error=Base de datos no disponible')
        
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        usuario = db.usuarios.find_one({'email': email})
        
        if not usuario or not check_password_hash(usuario.get('password_hash', ''), password):
            return redirect('/login?error=Email o contraseña incorrectos')
        
        if not usuario.get('email_verificado', False):
            session['email_pendiente'] = email
            session['usuario_id_pendiente'] = str(usuario['_id'])
            return redirect('/verify_email?error=Por favor verifica tu email primero')
        
        # Iniciar sesión
        user = User(
            str(usuario['_id']),
            usuario['email'],
            usuario.get('nombre', ''),
            usuario.get('email_verificado', False)
        )
        login_user(user, remember=True)
        
        # Verificar si hay una invitación pendiente
        invitacion_id = request.args.get('invitacion_id') or session.get('invitacion_pendiente')
        
        if invitacion_id:
            # Limpiar sesión de invitación
            session.pop('invitacion_pendiente', None)
            # Aceptar invitación automáticamente
            try:
                invitacion = db.invitaciones.find_one({'_id': ObjectId(invitacion_id)})
                if invitacion and invitacion.get('email_invitado', '').lower() == email.lower():
                    db.invitaciones.update_one(
                        {'_id': ObjectId(invitacion_id)},
                        {'$set': {
                            'estado': 'aceptada',
                            'fecha_aceptacion': datetime.now(),
                            'usuario_invitado_id': str(usuario['_id'])
                        }}
                    )
                    return redirect('/?success=Invitación aceptada&section=settings')
            except:
                pass
        
        return redirect('/')
    
    # GET: Mostrar formulario de login
    error = request.args.get('error', '')
    mensaje = request.args.get('mensaje', '')
    return render_template_string(AUTH_TEMPLATES['login'], error=error, mensaje=mensaje)

@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    return redirect('/login?mensaje=Sesión cerrada correctamente')

# ===== RUTAS DE INVITACIONES =====

@app.route('/invite', methods=['POST'])
@login_required
def invite_user():
    """Invitar usuario a compartir finanzas (por email, no requiere que exista)"""
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    email_invitado = request.form.get('email', '').strip().lower()
    permiso = request.form.get('permiso', 'ver')  # 'ver' o 'editar'
    
    if permiso not in ['ver', 'editar']:
        permiso = 'ver'
    
    # Validar email
    if not email_invitado or '@' not in email_invitado:
        return redirect('/?error=Email inválido&section=settings')
    
    if email_invitado == current_user.email.lower():
        return redirect('/?error=No puedes invitarte a ti mismo&section=settings')
    
    # Verificar si el usuario invitado existe
    usuario_invitado = db.usuarios.find_one({'email': email_invitado})
    usuario_invitado_id = None
    
    if usuario_invitado:
        usuario_invitado_id = str(usuario_invitado['_id'])
        
        # Verificar si ya existe una invitación activa
        invitacion_existente = db.invitaciones.find_one({
            'usuario_propietario_id': str(current_user.id),
            'usuario_invitado_id': usuario_invitado_id,
            'estado': {'$in': ['pendiente', 'aceptada']}
        })
        
        if invitacion_existente:
            return redirect('/?error=Ya existe una invitación para este usuario&section=settings')
    
    # Crear invitación (puede ser solo por email si el usuario no existe aún)
    invitacion = {
        'usuario_propietario_id': str(current_user.id),
        'email_invitado': email_invitado,
        'permiso': permiso,
        'estado': 'pendiente',
        'created_at': datetime.now()
    }
    
    if usuario_invitado_id:
        invitacion['usuario_invitado_id'] = usuario_invitado_id
    
    resultado = db.invitaciones.insert_one(invitacion)
    invitacion_id = str(resultado.inserted_id)
    
    # Enviar email de invitación
    try:
        url_aceptacion = f"{request.host_url}accept_invitation?invitacion_id={invitacion_id}"
        nota_usuario = ""
        if not usuario_invitado:
            nota_usuario = "<p style='color: #666; font-size: 12px; margin-top: 20px;'><strong>Nota:</strong> Si no tienes cuenta, deberás crear una para aceptar la invitación.</p>"
        
        msg = Message(
            subject=f'{current_user.nombre or current_user.email} te ha invitado a compartir finanzas',
            recipients=[email_invitado],
            html=f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">🐱 Finanzas Gatunas</h2>
                <p>{current_user.nombre or current_user.email} te ha invitado a {'ver y editar' if permiso == 'editar' else 'ver'} sus finanzas.</p>
                <p><a href="{url_aceptacion}" 
                      style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">
                    Aceptar Invitación
                </a></p>
                <p>O copia este enlace en tu navegador:</p>
                <p style="color: #666; font-size: 12px;">{url_aceptacion}</p>
                {nota_usuario}
            </body>
            </html>
            """
        )
        mail.send(msg)
    except Exception as e:
        print(f"[ERROR] Error enviando email de invitación: {e}")
    
    return redirect('/?success=Invitación enviada&section=settings')

@app.route('/accept_invitation')
def accept_invitation():
    """Aceptar invitación (puede requerir login o registro)"""
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    invitacion_id = request.args.get('invitacion_id')
    
    if not invitacion_id:
        return redirect('/login?error=Invitación no encontrada')
    
    try:
        invitacion = db.invitaciones.find_one({'_id': ObjectId(invitacion_id)})
        
        if not invitacion:
            return redirect('/login?error=Invitación no encontrada')
        
        if invitacion['estado'] == 'aceptada':
            # Si el usuario está logueado, redirigir a settings
            if current_user.is_authenticated:
                return redirect('/?mensaje=Invitación ya aceptada&section=settings')
            return redirect('/login?mensaje=Invitación ya aceptada')
        
        # Si el usuario no está logueado, redirigir a login/registro
        if not current_user.is_authenticated:
            # Guardar invitación_id en sesión para aceptarla después del login
            session['invitacion_pendiente'] = invitacion_id
            email_invitado = invitacion.get('email_invitado')
            
            # Verificar si el usuario existe
            usuario = db.usuarios.find_one({'email': email_invitado})
            
            if usuario:
                # Usuario existe, redirigir a login
                return redirect(f'/login?invitacion_id={invitacion_id}&mensaje=Inicia sesión para aceptar la invitación')
            else:
                # Usuario no existe, redirigir a registro
                return redirect(f'/register?invitacion_id={invitacion_id}&email={email_invitado}&mensaje=Crea una cuenta para aceptar la invitación')
        
        # Usuario está logueado, verificar que es el correcto
        email_invitado = invitacion.get('email_invitado')
        if current_user.email.lower() != email_invitado.lower():
            return redirect('/?error=Esta invitación no es para ti&section=settings')
        
        # Actualizar invitación con el ID del usuario si no lo tenía
        update_data = {
            'estado': 'aceptada',
            'fecha_aceptacion': datetime.now()
        }
        
        if 'usuario_invitado_id' not in invitacion:
            update_data['usuario_invitado_id'] = str(current_user.id)
        
        db.invitaciones.update_one(
            {'_id': ObjectId(invitacion_id)},
            {'$set': update_data}
        )
        
        # Limpiar sesión
        session.pop('invitacion_pendiente', None)
        
        return redirect('/?success=Invitación aceptada&section=settings')
    except Exception as e:
        return redirect(f'/login?error=Error al aceptar invitación: {str(e)}')

@app.route('/reject_invitation/<invitacion_id>')
@login_required
def reject_invitation(invitacion_id):
    """Rechazar invitación"""
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    try:
        invitacion = db.invitaciones.find_one({'_id': ObjectId(invitacion_id)})
        
        if invitacion and str(invitacion['usuario_invitado_id']) == str(current_user.id):
            db.invitaciones.delete_one({'_id': ObjectId(invitacion_id)})
        
        return redirect('/?success=Invitación rechazada&section=settings')
    except:
        return redirect('/?error=Error al rechazar invitación')

@app.route('/remove_invitation/<invitacion_id>')
@login_required
def remove_invitation(invitacion_id):
    """Eliminar invitación (solo propietario)"""
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    try:
        invitacion = db.invitaciones.find_one({'_id': ObjectId(invitacion_id)})
        
        if invitacion and str(invitacion['usuario_propietario_id']) == str(current_user.id):
            db.invitaciones.delete_one({'_id': ObjectId(invitacion_id)})
        
        return redirect('/?success=Invitación eliminada&section=settings')
    except:
        return redirect('/?error=Error al eliminar invitación')

@app.route('/')
@login_required
def home():
    """Página principal con dashboard de finanzas"""
    try:
        usuario_id = obtener_usuario_actual_id()
        if not usuario_id:
            return redirect('/login?error=Sesión inválida')
        
        # Obtener parámetros de filtro
        filtros = {}
        if request.args.get('filter_tipo'):
            filtros['tipo'] = request.args.get('filter_tipo')
        if request.args.get('filter_categoria'):
            filtros['categoria_id'] = request.args.get('filter_categoria')
        if request.args.get('filter_tarjeta'):
            filtros['tarjeta_id'] = request.args.get('filter_tarjeta')
        if request.args.get('filter_fecha_inicio'):
            filtros['fecha_inicio'] = request.args.get('filter_fecha_inicio')
        if request.args.get('filter_fecha_fin'):
            filtros['fecha_fin'] = request.args.get('filter_fecha_fin')
        if request.args.get('filter_descripcion'):
            filtros['descripcion'] = request.args.get('filter_descripcion')
        
        # Obtener datos
        balance = get_balance(usuario_id)
        categorias = get_categories(usuario_id)
        tarjetas = get_tarjetas(usuario_id)
        membresias = get_membresias(usuario_id)
        presupuestos = get_presupuestos(usuario_id=usuario_id)
        recordatorios = get_recordatorios(usuario_id)
        transacciones = get_transactions(filtros, usuario_id)
        dashboard_stats = get_dashboard_stats(usuario_id)
        
        # Obtener invitaciones pendientes y aceptadas
        invitaciones_pendientes = []
        invitaciones_enviadas = []
        invitaciones_aceptadas = []
        if db is not None:
            try:
                # Invitaciones recibidas pendientes
                invitaciones_pendientes = list(db.invitaciones.find({
                    'usuario_invitado_id': str(current_user.id),
                    'estado': 'pendiente'
                }))
                invitaciones_pendientes = convert_list_to_dicts(invitaciones_pendientes)
                for inv in invitaciones_pendientes:
                    try:
                        propietario_id = inv.get('usuario_propietario_id')
                        if propietario_id:
                            propietario = db.usuarios.find_one({'_id': ObjectId(propietario_id)})
                            if propietario:
                                inv['propietario_email'] = propietario.get('email')
                                inv['propietario_nombre'] = propietario.get('nombre')
                    except Exception as e:
                        print(f"[ERROR] Error procesando invitación pendiente: {e}")
                        continue
                
                # Invitaciones enviadas por el usuario
                invitaciones_enviadas = list(db.invitaciones.find({
                    'usuario_propietario_id': str(current_user.id)
                }))
                invitaciones_enviadas = convert_list_to_dicts(invitaciones_enviadas)
                for inv in invitaciones_enviadas:
                    try:
                        # Puede que no tenga usuario_invitado_id si aún no se registró
                        invitado_id = inv.get('usuario_invitado_id')
                        if invitado_id:
                            invitado = db.usuarios.find_one({'_id': ObjectId(invitado_id)})
                            if invitado:
                                inv['invitado_email'] = invitado.get('email')
                                inv['invitado_nombre'] = invitado.get('nombre')
                        else:
                            # Si no tiene usuario_invitado_id, usar email_invitado
                            inv['invitado_email'] = inv.get('email_invitado', 'Pendiente')
                            inv['invitado_nombre'] = 'Pendiente'
                    except Exception as e:
                        print(f"[ERROR] Error procesando invitación enviada: {e}")
                        # Si falla, usar email_invitado si existe
                        if 'email_invitado' in inv:
                            inv['invitado_email'] = inv['email_invitado']
                            inv['invitado_nombre'] = 'Pendiente'
                        continue
                
                # Invitaciones aceptadas (usuarios que comparten finanzas conmigo)
                invitaciones_aceptadas = list(db.invitaciones.find({
                    'usuario_invitado_id': str(current_user.id),
                    'estado': 'aceptada'
                }))
                invitaciones_aceptadas = convert_list_to_dicts(invitaciones_aceptadas)
                for inv in invitaciones_aceptadas:
                    try:
                        propietario_id = inv.get('usuario_propietario_id')
                        if propietario_id:
                            propietario = db.usuarios.find_one({'_id': ObjectId(propietario_id)})
                            if propietario:
                                inv['propietario_email'] = propietario.get('email')
                                inv['propietario_nombre'] = propietario.get('nombre')
                    except Exception as e:
                        print(f"[ERROR] Error procesando invitación aceptada: {e}")
                        continue
            except Exception as e:
                print(f"[ERROR] Error obteniendo invitaciones: {e}")
        
        # Calcular total del filtro
        total_filtrado = 0
        filtros_aplicados = None
        if filtros:
            filtros_aplicados = filtros
            try:
                for t in transacciones:
                    if filtros.get('tipo') == 'ingreso':
                        total_filtrado += t.get('monto', 0)
                    elif filtros.get('tipo') == 'gasto':
                        total_filtrado += t.get('monto', 0)
                    else:
                        total_filtrado += t.get('monto', 0) if t.get('tipo') == 'ingreso' else -t.get('monto', 0)
            except Exception as e:
                print(f"[ERROR] Error calculando total filtrado: {e}")
        
        # Crear gráfica
        chart_type = request.args.get('chart_type', 'gastos_por_categoria')
        chart_data = create_chart(transacciones, chart_type)
        
        return render_template_string(MAIN_PAGE_HTML,
                                    balance=balance,
                                    categorias=categorias,
                                    tarjetas=tarjetas,
                                    membresias=membresias,
                                    presupuestos=presupuestos,
                                    recordatorios=recordatorios,
                                    transacciones=transacciones,
                                    filtros_aplicados=filtros_aplicados,
                                    total_filtrado=total_filtrado,
                                    chart_data=chart_data,
                                    dashboard_stats=dashboard_stats,
                                    invitaciones_pendientes=invitaciones_pendientes,
                                    invitaciones_enviadas=invitaciones_enviadas,
                                    invitaciones_aceptadas=invitaciones_aceptadas,
                                    usuario_actual=current_user,
                                    today=datetime.now().strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"[ERROR] Error en home(): {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Error interno del servidor</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>", 500

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    """Agregar nueva transacción"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=transactions')
        
        usuario_id = obtener_usuario_actual_id()
        transaccion = {
            'descripcion': request.form['descripcion'],
            'monto': float(request.form['monto']),
            'tipo': request.form['tipo'],
            'categoria_id': request.form['categoria_id'] or None,
            'tarjeta_id': request.form['tarjeta_id'] or None,
            'fecha': request.form['fecha'],
            'notas': request.form.get('notas') or None,
            'cuotas': 1,
            'cuota_actual': 1,
            'usuario_id': usuario_id,
            'created_at': datetime.now()
        }
        
        db.transacciones.insert_one(transaccion)
        
        return redirect('/?success=1&section=transactions')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=transactions')

@app.route('/edit_transaction/<id>')
@login_required
def edit_transaction(id):
    """Editar transacción"""
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    try:
        transaction = db.transacciones.find_one({'_id': ObjectId(id)})
    except:
        transaction = None
    
    if not transaction:
        return redirect('/?error=Transacción no encontrada')
    
    # Por ahora redirigimos a la página principal con un mensaje
    # En una versión futura podríamos crear un formulario de edición
    return redirect('/?edit_id=' + str(id))

@app.route('/delete_transaction/<id>')
@login_required
def delete_transaction(id):
    """Eliminar transacción"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=list')
        
        try:
            db.transacciones.delete_one({'_id': ObjectId(id)})
        except:
            return redirect('/?error=Transacción no encontrada&section=list')
        
        return redirect('/?deleted=1&section=list')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=list')

@app.route('/export_csv')
def export_csv():
    """Exportar transacciones a CSV"""
    try:
        transacciones = get_transactions()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Encabezados
        writer.writerow(['Fecha', 'Descripción', 'Categoría', 'Método de Pago', 'Monto', 'Tipo', 'Notas'])
        
        # Datos
        for t in transacciones:
            writer.writerow([
                t['fecha'],
                t['descripcion'],
                t['categoria_nombre'] or 'Sin categoría',
                t['tarjeta_nombre'] or 'No especificado',
                t['monto'],
                t['tipo'],
                t['notas'] or ''
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=finanzas_gatunas.csv'}
        )
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/export_json')
def export_json():
    """Exportar transacciones a JSON"""
    try:
        transacciones = get_transactions()
        
        # Convertir a lista de diccionarios
        data = []
        for t in transacciones:
            data.append({
                'id': t['id'],
                'fecha': t['fecha'],
                'descripcion': t['descripcion'],
                'categoria': t['categoria_nombre'] or 'Sin categoría',
                'metodo_pago': t['tarjeta_nombre'] or 'No especificado',
                'monto': t['monto'],
                'tipo': t['tipo'],
                'notas': t['notas'] or '',
                'created_at': t['created_at']
            })
        
        from flask import Response
        return Response(
            json.dumps(data, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=finanzas_gatunas.json'}
        )
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/health')
def health():
    """Healthcheck para Railway"""
    return jsonify({
        'status': 'healthy',
        'message': '¡Aplicación de finanzas funcionando perfectamente! 🐱',
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

# ===== RUTAS PARA MEMBRESÍAS =====

@app.route('/add_membresia', methods=['POST'])
@login_required
def add_membresia():
    """Agregar nueva membresía"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=membresias')
        
        usuario_id = obtener_usuario_actual_id()
        membresia = {
            'nombre': request.form['nombre'],
            'plataforma': request.form.get('plataforma') or None,
            'tipo': request.form.get('tipo') or None,
            'monto_mensual': float(request.form['monto_mensual']),
            'monto_anual': float(request.form.get('monto_anual', 0) or 0),
            'tarjeta_id': request.form['tarjeta_id'] or None,
            'fecha_inicio': request.form['fecha_inicio'],
            'fecha_renovacion': request.form['fecha_renovacion'],
            'estado': request.form.get('estado', 'activa'),
            'notas': request.form.get('notas') or None,
            'usuario_id': usuario_id,
            'created_at': datetime.now()
        }
        
        db.membresias.insert_one(membresia)
        
        return redirect('/?success=1&section=membresias')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=membresias')

@app.route('/edit_membresia/<id>', methods=['GET', 'POST'])
@login_required
def edit_membresia(id):
    """Editar membresía"""
    if request.method == 'POST':
        try:
            if db is None:
                return redirect('/?error=Base de datos no disponible&section=membresias')
            
            update_data = {
                'nombre': request.form['nombre'],
                'plataforma': request.form['plataforma'],
                'tipo': request.form['tipo'],
                'monto_mensual': float(request.form['monto_mensual']),
                'monto_anual': float(request.form['monto_anual']) if request.form.get('monto_anual') else None,
                'tarjeta_id': request.form['tarjeta_id'] or None,
                'fecha_inicio': request.form['fecha_inicio'],
                'fecha_renovacion': request.form['fecha_renovacion'],
                'notas': request.form.get('notas')
            }
            
            try:
                db.membresias.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            except:
                return redirect('/?error=Membresía no encontrada&section=membresias')
            
            return redirect('/?success=membresia_editada&section=membresias')
        except Exception as e:
            return redirect('/?error=' + str(e) + '&section=membresias')
    
    # GET: Mostrar formulario de edición
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    try:
        membresia = db.membresias.find_one({'_id': ObjectId(id)})
    except:
        membresia = None
    
    if not membresia:
        return redirect('/?error=Membresía no encontrada')
    
    return redirect('/?edit_membresia_id=' + str(id))

@app.route('/delete_membresia/<id>')
@login_required
def delete_membresia(id):
    """Eliminar membresía"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=membresias')
        
        try:
            db.membresias.delete_one({'_id': ObjectId(id)})
        except:
            return redirect('/?error=Membresía no encontrada&section=membresias')
        
        return redirect('/?success=membresia_eliminada&section=membresias')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=membresias')

# ===== RUTAS PARA TARJETAS =====

@app.route('/add_tarjeta', methods=['POST'])
@login_required
def add_tarjeta():
    """Agregar nueva tarjeta"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=tarjetas')
        
        usuario_id = obtener_usuario_actual_id()
        tarjeta = {
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'banco': request.form.get('banco'),
            'limite_credito': float(request.form['limite_credito']) if request.form.get('limite_credito') else 0,
            'fecha_vencimiento': request.form.get('fecha_vencimiento'),
            'color': request.form.get('color', '#667eea'),
            'icono': request.form.get('icono', '💳'),
            'activa': True,
            'usuario_id': usuario_id,
            'created_at': datetime.now()
        }
        
        db.tarjetas.insert_one(tarjeta)
        
        return redirect('/?success=tarjeta_agregada&section=tarjetas')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=tarjetas')

@app.route('/edit_tarjeta/<id>', methods=['GET', 'POST'])
@login_required
def edit_tarjeta(id):
    """Editar tarjeta"""
    if request.method == 'POST':
        try:
            if db is None:
                return redirect('/?error=Base de datos no disponible&section=tarjetas')
            
            update_data = {
                'nombre': request.form['nombre'],
                'tipo': request.form['tipo'],
                'banco': request.form.get('banco'),
                'limite_credito': float(request.form['limite_credito']) if request.form.get('limite_credito') else 0,
                'fecha_vencimiento': request.form.get('fecha_vencimiento'),
                'color': request.form.get('color', '#667eea'),
                'icono': request.form.get('icono', '💳')
            }
            
            try:
                db.tarjetas.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            except:
                return redirect('/?error=Tarjeta no encontrada&section=tarjetas')
            
            return redirect('/?success=tarjeta_editada&section=tarjetas')
        except Exception as e:
            return redirect('/?error=' + str(e) + '&section=tarjetas')
    
    # GET: Mostrar formulario de edición
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    try:
        tarjeta = db.tarjetas.find_one({'_id': ObjectId(id)})
    except:
        tarjeta = None
    
    if not tarjeta:
        return redirect('/?error=Tarjeta no encontrada')
    
    return redirect('/?edit_tarjeta_id=' + str(id))

@app.route('/delete_tarjeta/<id>')
@login_required
def delete_tarjeta(id):
    """Eliminar tarjeta"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=tarjetas')
        
        try:
            db.tarjetas.delete_one({'_id': ObjectId(id)})
        except:
            return redirect('/?error=Tarjeta no encontrada&section=tarjetas')
        
        return redirect('/?success=tarjeta_eliminada&section=tarjetas')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=tarjetas')

# ===== RUTAS PARA PRESUPUESTOS =====

@app.route('/add_presupuesto', methods=['POST'])
@login_required
def add_presupuesto():
    """Agregar nuevo presupuesto"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=presupuestos')
        
        usuario_id = obtener_usuario_actual_id()
        presupuesto = {
            'mes': request.form['mes'],
            'año': int(request.form['año']),
            'categoria_id': request.form['categoria_id'],
            'monto_planificado': float(request.form['monto_planificado']),
            'monto_gastado': 0,
            'usuario_id': usuario_id,
            'created_at': datetime.now()
        }
        
        db.presupuestos.insert_one(presupuesto)
        
        return redirect('/?success=presupuesto_agregado&section=presupuestos')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=presupuestos')

@app.route('/edit_presupuesto/<id>', methods=['GET', 'POST'])
@login_required
def edit_presupuesto(id):
    """Editar presupuesto"""
    if request.method == 'POST':
        try:
            if db is None:
                return redirect('/?error=Base de datos no disponible&section=presupuestos')
            
            update_data = {
                'mes': request.form['mes'],
                'año': int(request.form['año']),
                'categoria_id': request.form['categoria_id'],
                'monto_planificado': float(request.form['monto_planificado'])
            }
            
            try:
                db.presupuestos.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            except:
                return redirect('/?error=Presupuesto no encontrado&section=presupuestos')
            
            return redirect('/?success=presupuesto_editado&section=presupuestos')
        except Exception as e:
            return redirect('/?error=' + str(e) + '&section=presupuestos')
    
    # GET: Mostrar formulario de edición
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    try:
        presupuesto = db.presupuestos.find_one({'_id': ObjectId(id)})
    except:
        presupuesto = None
    
    if not presupuesto:
        return redirect('/?error=Presupuesto no encontrado')
    
    return redirect('/?edit_presupuesto_id=' + str(id))

@app.route('/delete_presupuesto/<id>')
@login_required
def delete_presupuesto(id):
    """Eliminar presupuesto"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=presupuestos')
        
        try:
            db.presupuestos.delete_one({'_id': ObjectId(id)})
        except:
            return redirect('/?error=Presupuesto no encontrado&section=presupuestos')
        
        return redirect('/?success=presupuesto_eliminado&section=presupuestos')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=presupuestos')

# ===== RUTAS PARA RECORDATORIOS =====

@app.route('/add_recordatorio', methods=['POST'])
@login_required
def add_recordatorio():
    """Agregar nuevo recordatorio"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=recordatorios')
        
        usuario_id = obtener_usuario_actual_id()
        # El formulario usa 'descripcion', lo usamos como 'titulo' si no hay 'titulo'
        descripcion = request.form.get('descripcion', '')
        titulo = request.form.get('titulo') or descripcion
        
        recordatorio = {
            'titulo': titulo,
            'descripcion': request.form.get('descripcion') or titulo,
            'monto': float(request.form['monto']),
            'fecha_vencimiento': request.form['fecha_vencimiento'],
            'tarjeta_id': request.form['tarjeta_id'] or None,
            'categoria_id': request.form['categoria_id'] or None,
            'estado': 'pendiente',
            'prioridad': request.form.get('prioridad', 'normal'),
            'usuario_id': usuario_id,
            'created_at': datetime.now()
        }
        
        db.recordatorios.insert_one(recordatorio)
        
        return redirect('/?success=recordatorio_agregado&section=recordatorios')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=recordatorios')

@app.route('/edit_recordatorio/<id>', methods=['GET', 'POST'])
@login_required
def edit_recordatorio(id):
    """Editar recordatorio"""
    if request.method == 'POST':
        try:
            if db is None:
                return redirect('/?error=Base de datos no disponible&section=recordatorios')
            
            update_data = {
                'titulo': request.form['titulo'],
                'descripcion': request.form.get('descripcion'),
                'monto': float(request.form['monto']),
                'fecha_vencimiento': request.form['fecha_vencimiento'],
                'tarjeta_id': request.form['tarjeta_id'] or None,
                'categoria_id': request.form['categoria_id'] or None,
                'prioridad': request.form.get('prioridad', 'normal')
            }
            
            try:
                db.recordatorios.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            except:
                return redirect('/?error=Recordatorio no encontrado&section=recordatorios')
            
            return redirect('/?success=recordatorio_editado&section=recordatorios')
        except Exception as e:
            return redirect('/?error=' + str(e) + '&section=recordatorios')
    
    # GET: Mostrar formulario de edición
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    try:
        recordatorio = db.recordatorios.find_one({'_id': ObjectId(id)})
    except:
        recordatorio = None
    
    if not recordatorio:
        return redirect('/?error=Recordatorio no encontrado')
    
    return redirect('/?edit_recordatorio_id=' + str(id))

@app.route('/delete_recordatorio/<id>')
@login_required
def delete_recordatorio(id):
    """Eliminar recordatorio"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=recordatorios')
        
        try:
            db.recordatorios.delete_one({'_id': ObjectId(id)})
        except:
            return redirect('/?error=Recordatorio no encontrado&section=recordatorios')
        
        return redirect('/?success=recordatorio_eliminado&section=recordatorios')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=recordatorios')

@app.route('/completar_recordatorio/<id>')
def completar_recordatorio(id):
    """Marcar recordatorio como completado"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=recordatorios')
        
        try:
            db.recordatorios.update_one({'_id': ObjectId(id)}, {'$set': {'estado': 'completado'}})
        except:
            return redirect('/?error=Recordatorio no encontrado&section=recordatorios')
        
        return redirect('/?success=recordatorio_completado&section=recordatorios')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=recordatorios')

# ===== RUTAS PARA CATEGORÍAS =====

@app.route('/add_categoria', methods=['POST'])
def add_categoria():
    """Agregar nueva categoría"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=transactions')
        
        categoria = {
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'color': request.form.get('color', '#667eea'),
            'icono': request.form.get('icono', '💰'),
            'presupuesto_mensual': float(request.form.get('presupuesto_mensual', 0)),
            'activa': True,
            'created_at': datetime.now()
        }
        
        db.categorias.insert_one(categoria)
        
        return redirect('/?success=categoria_agregada&section=transactions')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=transactions')

@app.route('/edit_categoria/<id>', methods=['GET', 'POST'])
def edit_categoria(id):
    """Editar categoría"""
    if request.method == 'POST':
        try:
            if db is None:
                return redirect('/?error=Base de datos no disponible&section=transactions')
            
            update_data = {
                'nombre': request.form['nombre'],
                'tipo': request.form['tipo'],
                'color': request.form.get('color', '#667eea'),
                'icono': request.form.get('icono', '💰'),
                'presupuesto_mensual': float(request.form.get('presupuesto_mensual', 0))
            }
            
            try:
                db.categorias.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            except:
                return redirect('/?error=Categoría no encontrada&section=transactions')
            
            return redirect('/?success=categoria_editada&section=transactions')
        except Exception as e:
            return redirect('/?error=' + str(e) + '&section=transactions')
    
    # GET: Mostrar formulario de edición
    if db is None:
        return redirect('/?error=Base de datos no disponible')
    
    try:
        categoria = db.categorias.find_one({'_id': ObjectId(id)})
    except:
        categoria = None
    
    if not categoria:
        return redirect('/?error=Categoría no encontrada')
    
    return redirect('/?edit_categoria_id=' + str(id))

@app.route('/delete_categoria/<id>')
def delete_categoria(id):
    """Eliminar categoría"""
    try:
        if db is None:
            return redirect('/?error=Base de datos no disponible&section=transactions')
        
        try:
            db.categorias.delete_one({'_id': ObjectId(id)})
        except:
            return redirect('/?error=Categoría no encontrada&section=transactions')
        
        return redirect('/?success=categoria_eliminada&section=transactions')
    except Exception as e:
        return redirect('/?error=' + str(e) + '&section=transactions')

# ===== HANDLER DE ERRORES GLOBAL =====

@app.errorhandler(500)
def internal_error(error):
    """Manejar errores internos del servidor"""
    import traceback
    error_info = traceback.format_exc()
    print(f"[ERROR] Error 500: {error}")
    print(f"[ERROR] Traceback:\n{error_info}")
    return f"<h1>Error interno del servidor</h1><p>Ocurrió un error inesperado. Por favor inténtalo de nuevo.</p><pre>{error_info}</pre>", 500

@app.errorhandler(404)
def not_found(error):
    """Manejar errores 404"""
    return "<h1>Página no encontrada</h1><p>La página que buscas no existe.</p>", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"[INFO] Iniciando aplicacion de finanzas en puerto {port}")
    print(f"[INFO] Abre tu navegador en: http://localhost:{port}")
    print(f"[INFO] Presiona Ctrl+C para detener")
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print(f"\n[INFO] Aplicacion detenida")
