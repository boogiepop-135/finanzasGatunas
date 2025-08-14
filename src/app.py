#!/usr/bin/env python3
"""
Aplicación de Finanzas del Hogar - Finanzas Gatunas
"""
from flask import Flask, jsonify, render_template_string, request, redirect, url_for
import os
import sqlite3
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

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'finanzas-gatunas-secret-key')

# Configuración de la base de datos
DATABASE = 'finanzas.db'

def init_db():
    """Inicializar la base de datos"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabla de tarjetas de crédito/débito
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarjetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            banco TEXT,
            limite_credito REAL,
            fecha_vencimiento DATE,
            color TEXT DEFAULT '#667eea',
            icono TEXT DEFAULT '💳',
            activa BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de categorías personalizables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL,
            color TEXT DEFAULT '#667eea',
            icono TEXT DEFAULT '💰',
            presupuesto_mensual REAL DEFAULT 0,
            activa BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de membresías y suscripciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membresias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            plataforma TEXT NOT NULL,
            tipo TEXT NOT NULL,
            monto_mensual REAL NOT NULL,
            monto_anual REAL,
            tarjeta_id INTEGER,
            fecha_inicio DATE NOT NULL,
            fecha_renovacion DATE,
            estado TEXT DEFAULT 'activa',
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tarjeta_id) REFERENCES tarjetas (id)
        )
    ''')
    
    # Tabla de transacciones mejorada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            tipo TEXT NOT NULL,
            categoria_id INTEGER,
            tarjeta_id INTEGER,
            fecha DATE NOT NULL,
            fecha_vencimiento DATE,
            cuotas INTEGER DEFAULT 1,
            cuota_actual INTEGER DEFAULT 1,
            notas TEXT,
            comprobante_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id),
            FOREIGN KEY (tarjeta_id) REFERENCES tarjetas (id)
        )
    ''')
    
    # Tabla de presupuestos mensuales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            año INTEGER NOT NULL,
            categoria_id INTEGER,
            monto_planificado REAL NOT NULL,
            monto_gastado REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id),
            UNIQUE(mes, año, categoria_id)
        )
    ''')
    
    # Tabla de recordatorios de pagos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recordatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            monto REAL NOT NULL,
            fecha_vencimiento DATE NOT NULL,
            tarjeta_id INTEGER,
            categoria_id INTEGER,
            estado TEXT DEFAULT 'pendiente',
            prioridad TEXT DEFAULT 'normal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tarjeta_id) REFERENCES tarjetas (id),
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
    ''')
    
    # Insertar tarjetas por defecto
    tarjetas_default = [
        ('Efectivo', 'efectivo', 'N/A', 0, None, '#4CAF50', '💵'),
        ('Débito Principal', 'debito', 'Banco Local', 0, None, '#2196F3', '🏦'),
        ('Crédito Visa', 'credito', 'Banco Principal', 50000, '2026-12-31', '#9C27B0', '💳'),
        ('Crédito Mastercard', 'credito', 'Banco Secundario', 30000, '2026-06-30', '#FF9800', '💳')
    ]
    
    for tarjeta in tarjetas_default:
        try:
            cursor.execute('''
                INSERT INTO tarjetas (nombre, tipo, banco, limite_credito, fecha_vencimiento, color, icono)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', tarjeta)
        except sqlite3.IntegrityError:
            pass
    
    # Insertar categorías por defecto
    categorias_default = [
        ('Ingresos', 'ingreso', '#4CAF50', '💰'),
        ('Salario', 'ingreso', '#4CAF50', '💼'),
        ('Freelance', 'ingreso', '#4CAF50', '💻'),
        ('Inversiones', 'ingreso', '#4CAF50', '📈'),
        ('Alimentación', 'gasto', '#FF5722', '🍽️'),
        ('Transporte', 'gasto', '#2196F3', '🚗'),
        ('Vivienda', 'gasto', '#9C27B0', '🏠'),
        ('Entretenimiento', 'gasto', '#FF9800', '🎮'),
        ('Salud', 'gasto', '#E91E63', '🏥'),
        ('Educación', 'gasto', '#607D8B', '📚'),
        ('Ropa', 'gasto', '#795548', '👕'),
        ('Membresías', 'gasto', '#FF5722', '🎫'),
        ('Servicios', 'gasto', '#3F51B5', '🔌'),
        ('Otros', 'gasto', '#9E9E9E', '📦')
    ]
    
    for cat in categorias_default:
        try:
            cursor.execute('INSERT INTO categorias (nombre, tipo, color, icono) VALUES (?, ?, ?, ?)', cat)
        except sqlite3.IntegrityError:
            pass
    
    # Insertar membresías de ejemplo
    membresias_default = [
        ('Netflix', 'Netflix', 'streaming', 15.99, 191.88, 3, '2024-01-01', '2024-02-01'),
        ('Spotify', 'Spotify', 'musica', 9.99, 119.88, 3, '2024-01-01', '2024-02-01'),
        ('Gym', 'Local Gym', 'fitness', 29.99, 359.88, 2, '2024-01-01', '2024-02-01')
    ]
    
    for mem in membresias_default:
        try:
            cursor.execute('''
                INSERT INTO membresias (nombre, plataforma, tipo, monto_mensual, monto_anual, tarjeta_id, fecha_inicio, fecha_renovacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', mem)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_tarjetas():
    """Obtener todas las tarjetas"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tarjetas WHERE activa = 1 ORDER BY nombre')
    tarjetas = cursor.fetchall()
    conn.close()
    return tarjetas

def get_membresias():
    """Obtener todas las membresías"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.*, t.nombre as tarjeta_nombre, t.color as tarjeta_color, t.icono as tarjeta_icono
        FROM membresias m
        LEFT JOIN tarjetas t ON m.tarjeta_id = t.id
        ORDER BY m.fecha_renovacion ASC
    ''')
    membresias = cursor.fetchall()
    conn.close()
    return membresias

def get_presupuestos(mes=None, año=None):
    """Obtener presupuestos mensuales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if mes and año:
        cursor.execute('''
            SELECT p.*, c.nombre as categoria_nombre, c.color, c.icono
            FROM presupuestos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.mes = ? AND p.año = ?
            ORDER BY c.nombre
        ''', (mes, año))
    else:
        cursor.execute('''
            SELECT p.*, c.nombre as categoria_nombre, c.color, c.icono
            FROM presupuestos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.año DESC, p.mes DESC, c.nombre
        ''')
    
    presupuestos = cursor.fetchall()
    conn.close()
    return presupuestos

def get_recordatorios():
    """Obtener recordatorios de pagos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, t.nombre as tarjeta_nombre, c.nombre as categoria_nombre
        FROM recordatorios r
        LEFT JOIN tarjetas t ON r.tarjeta_id = t.id
        LEFT JOIN categorias c ON r.categoria_id = c.id
        WHERE r.estado = 'pendiente'
        ORDER BY r.fecha_vencimiento ASC
    ''')
    recordatorios = cursor.fetchall()
    conn.close()
    return recordatorios

def get_transactions(filtros=None):
    """Obtener transacciones con filtros"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT t.*, c.nombre as categoria_nombre, c.color, c.icono,
               tar.nombre as tarjeta_nombre, tar.color as tarjeta_color, tar.icono as tarjeta_icono
        FROM transacciones t
        LEFT JOIN categorias c ON t.categoria_id = c.id
        LEFT JOIN tarjetas tar ON t.tarjeta_id = tar.id
        WHERE 1=1
    '''
    params = []
    
    if filtros:
        if filtros.get('tipo'):
            query += ' AND t.tipo = ?'
            params.append(filtros['tipo'])
        
        if filtros.get('categoria_id'):
            query += ' AND t.categoria_id = ?'
            params.append(filtros['categoria_id'])
        
        if filtros.get('tarjeta_id'):
            query += ' AND t.tarjeta_id = ?'
            params.append(filtros['tarjeta_id'])
        
        if filtros.get('fecha_inicio'):
            query += ' AND t.fecha >= ?'
            params.append(filtros['fecha_inicio'])
        
        if filtros.get('fecha_fin'):
            query += ' AND t.fecha <= ?'
            params.append(filtros['fecha_fin'])
        
        if filtros.get('descripcion'):
            query += ' AND t.descripcion LIKE ?'
            params.append(f'%{filtros["descripcion"]}%')
    
    query += ' ORDER BY t.fecha DESC, t.created_at DESC'
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()
    
    return transactions

def get_balance():
    """Obtener balance total"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total ingresos
    cursor.execute('SELECT COALESCE(SUM(monto), 0) FROM transacciones WHERE tipo = "ingreso"')
    total_ingresos = cursor.fetchone()[0]
    
    # Total gastos
    cursor.execute('SELECT COALESCE(SUM(monto), 0) FROM transacciones WHERE tipo = "gasto"')
    total_gastos = cursor.fetchone()[0]
    
    # Total membresías mensuales
    cursor.execute('SELECT COALESCE(SUM(monto_mensual), 0) FROM membresias WHERE estado = "activa"')
    total_membresias = cursor.fetchone()[0]
    
    # Balance de tarjetas de crédito
    cursor.execute('''
        SELECT COALESCE(SUM(
            t.limite_credito - COALESCE((
                SELECT SUM(tr.monto) 
                FROM transacciones tr 
                WHERE tr.tarjeta_id = t.id AND tr.tipo = 'gasto'
            ), 0)
        ), 0)
        FROM tarjetas t
        WHERE t.tipo = 'credito' AND t.activa = 1
    ''')
    balance_credito = cursor.fetchone()[0]
    
    balance = total_ingresos - total_gastos
    
    conn.close()
    return {
        'ingresos': total_ingresos,
        'gastos': total_gastos,
        'balance': balance,
        'membresias_mensuales': total_membresias,
        'balance_credito': balance_credito
    }

def get_dashboard_stats():
    """Obtener estadísticas del dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Gastos por categoría este mes
    mes_actual = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT c.nombre, c.color, c.icono, COALESCE(SUM(t.monto), 0) as total
        FROM categorias c
        LEFT JOIN transacciones t ON c.id = t.categoria_id 
            AND t.tipo = 'gasto' 
            AND strftime('%Y-%m', t.fecha) = ?
        WHERE c.tipo = 'gasto' AND c.activa = 1
        GROUP BY c.id
        ORDER BY total DESC
        LIMIT 10
    ''', (mes_actual,))
    gastos_por_categoria = cursor.fetchall()
    
    # Próximos vencimientos de tarjetas
    cursor.execute('''
        SELECT nombre, fecha_vencimiento, limite_credito
        FROM tarjetas 
        WHERE tipo = 'credito' AND activa = 1
        ORDER BY fecha_vencimiento ASC
        LIMIT 5
    ''')
    proximos_vencimientos = cursor.fetchall()
    
    # Recordatorios urgentes
    cursor.execute('''
        SELECT titulo, fecha_vencimiento, monto, prioridad
        FROM recordatorios 
        WHERE estado = 'pendiente' AND fecha_vencimiento <= date('now', '+7 days')
        ORDER BY fecha_vencimiento ASC
        LIMIT 5
    ''')
    recordatorios_urgentes = cursor.fetchall()
    
    conn.close()
    
    return {
        'gastos_por_categoria': gastos_por_categoria,
        'proximos_vencimientos': proximos_vencimientos,
        'recordatorios_urgentes': recordatorios_urgentes
    }

def get_categories():
    """Obtener todas las categorías"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias ORDER BY nombre')
    categories = cursor.fetchall()
    conn.close()
    return categories

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
            
            # Calcular balance del mes
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COALESCE(SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE -monto END), 0)
                FROM transacciones 
                WHERE strftime('%Y-%m', fecha) = ?
            ''', (mes,))
            balance_mes = cursor.fetchone()[0]
            balances.insert(0, balance_mes)
            conn.close()
        
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
            </ul>
        </div>
        
        <!-- Contenido principal -->
        <div class="main-content">
            <div class="header">
                <h1>🐱 Finanzas Gatunas</h1>
                <p>Gestor completo de finanzas personales</p>
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
                    <div class="export-buttons">
                        <button class="btn btn-primary" onclick="showAddRecordatorioForm()">
                            <i class="fas fa-plus"></i> Nuevo Recordatorio
                        </button>
                    </div>
                    
                    <!-- Formulario para agregar recordatorio -->
                    <div id="addRecordatorioForm" class="section-card" style="display: none; margin-top: 20px;">
                        <h4><i class="fas fa-plus"></i> Crear Nuevo Recordatorio</h4>
                        <form method="POST" action="/add_recordatorio">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="recordatorio_titulo">Título *</label>
                                    <input type="text" id="recordatorio_titulo" name="titulo" required>
                                </div>
                                <div class="form-group">
                                    <label for="recordatorio_monto">Monto *</label>
                                    <input type="number" id="recordatorio_monto" name="monto" step="0.01" min="0" required>
                                </div>
                                <div class="form-group">
                                    <label for="recordatorio_prioridad">Prioridad</label>
                                    <select id="recordatorio_prioridad" name="prioridad">
                                        <option value="baja">Baja</option>
                                        <option value="normal" selected>Normal</option>
                                        <option value="alta">Alta</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="recordatorio_fecha">Fecha de Vencimiento *</label>
                                    <input type="date" id="recordatorio_fecha" name="fecha_vencimiento" required>
                                </div>
                                <div class="form-group">
                                    <label for="recordatorio_tarjeta">Tarjeta</label>
                                    <select id="recordatorio_tarjeta" name="tarjeta_id">
                                        <option value="">Seleccionar tarjeta</option>
                                        {% for tar in tarjetas %}
                                            <option value="{{ tar.id }}">{{ tar.icono }} {{ tar.nombre }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="recordatorio_categoria">Categoría</label>
                                    <select id="recordatorio_categoria" name="categoria_id">
                                        <option value="">Seleccionar categoría</option>
                                        {% for cat in categorias %}
                                            <option value="{{ cat.id }}">{{ cat.icono }} {{ cat.nombre }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="recordatorio_descripcion">Descripción</label>
                                    <textarea id="recordatorio_descripcion" name="descripcion" rows="2" placeholder="Descripción opcional del recordatorio"></textarea>
                                </div>
                            </div>
                            <div class="form-row">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i> Crear Recordatorio
                                </button>
                                <button type="button" class="btn btn-warning" onclick="hideAddRecordatorioForm()">
                                    <i class="fas fa-times"></i> Cancelar
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    {% if recordatorios %}
                    <table class="transactions-table">
                        <thead>
                            <tr>
                                <th>Título</th>
                                <th>Descripción</th>
                                <th>Monto</th>
                                <th>Vencimiento</th>
                                <th>Tarjeta</th>
                                <th>Categoría</th>
                                <th>Prioridad</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for r in recordatorios %}
                            <tr>
                                <td>{{ r.titulo }}</td>
                                <td>{{ r.descripcion or '-' }}</td>
                                <td>${{ "%.2f"|format(r.monto) }}</td>
                                <td>{{ r.fecha_vencimiento }}</td>
                                <td>{{ r.tarjeta_nombre or 'N/A' }}</td>
                                <td>{{ r.categoria_nombre or 'N/A' }}</td>
                                <td>
                                    <span class="transaction-type" style="background: {{ '#FF5722' if r.prioridad == 'alta' else '#FF9800' if r.prioridad == 'media' else '#4CAF50' }};">
                                        {{ r.prioridad.title() }}
                                    </span>
                                </td>
                                <td>
                                    <span class="transaction-type {{ r.estado }}">
                                        {{ r.estado.title() }}
                                    </span>
                                </td>
                                <td>
                                    <a href="/completar_recordatorio/{{ r.id }}" class="btn btn-success" style="padding: 6px 12px; font-size: 12px;" onclick="return confirm('¿Marcar como completado?')">
                                        <i class="fas fa-check"></i>
                                    </a>
                                    <button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="showEditRecordatorioForm({{ r.id }}, '{{ r.titulo }}', '{{ r.descripcion or '' }}', {{ r.monto }}, '{{ r.fecha_vencimiento }}', {{ r.tarjeta_id or 'null' }}, {{ r.categoria_id or 'null' }}, '{{ r.prioridad }}')">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <a href="/delete_recordatorio/{{ r.id }}" class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="return confirm('¿Estás seguro de eliminar este recordatorio?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <div class="empty-state">
                        <i class="fas fa-bell"></i>
                        <h4>No hay recordatorios</h4>
                        <p>Crea tu primer recordatorio de pago</p>
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
            document.getElementById(sectionId).classList.add('active');
            
            // Actualizar menú activo
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // Marcar el enlace activo
            event.target.classList.add('active');
        }
        
        // Cambiar tipo de transacción
        document.getElementById('tipo').addEventListener('change', function() {
            const tipo = this.value;
            const categoriaSelect = document.getElementById('categoria_id');
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
        });
        
        // Cambiar gráfica
        function changeChart(chartType) {
            window.location.href = '/?chart_type=' + chartType;
        }
        
        // Aplicar filtros automáticamente
        document.getElementById('filterForm').addEventListener('submit', function() {
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
        
        // Toggle sidebar en móvil
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('open');
        }
        
        // Cerrar sidebar al hacer clic fuera en móvil
        document.addEventListener('click', function(event) {
            const sidebar = document.getElementById('sidebar');
            const mobileToggle = document.querySelector('.mobile-menu-toggle');
            
            if (window.innerWidth <= 1024 && 
                !sidebar.contains(event.target) && 
                !mobileToggle.contains(event.target)) {
                sidebar.classList.remove('open');
            }
        });
        
        // ===== FUNCIONES PARA FORMULARIOS =====
        
        // Membresías
        function showAddMembresiaForm() {
            document.getElementById('addMembresiaForm').style.display = 'block';
            // Establecer fecha actual por defecto
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('membresia_fecha_inicio').value = today;
        }
        
        function hideAddMembresiaForm() {
            document.getElementById('addMembresiaForm').style.display = 'none';
        }
        
        function showEditMembresiaForm(id, nombre, plataforma, tipo, monto_mensual, monto_anual, tarjeta_id, fecha_inicio, fecha_renovacion, notas) {
            // Por ahora redirigimos a la página principal con parámetros de edición
            // En una versión futura podríamos mostrar un modal o formulario de edición
            window.location.href = '/?edit_membresia_id=' + id;
        }
        
                 // Tarjetas
         function showAddTarjetaForm() {
             document.getElementById('addTarjetaForm').style.display = 'block';
         }
         
         function hideAddTarjetaForm() {
             document.getElementById('addTarjetaForm').style.display = 'none';
         }
         
         function showEditTarjetaForm(id, nombre, tipo, banco, limite_credito, fecha_vencimiento, color, icono) {
             // Actualizar la acción del formulario con el ID correcto
             document.getElementById('editTarjetaFormElement').action = '/edit_tarjeta/' + id;
             
             // Llenar los campos con los datos actuales
             document.getElementById('edit_tarjeta_nombre').value = nombre;
             document.getElementById('edit_tarjeta_tipo').value = tipo;
             document.getElementById('edit_tarjeta_banco').value = banco;
             document.getElementById('edit_tarjeta_limite').value = limite_credito;
             document.getElementById('edit_tarjeta_vencimiento').value = fecha_vencimiento;
             document.getElementById('edit_tarjeta_color').value = color;
             document.getElementById('edit_tarjeta_icono').value = icono;
             
             // Mostrar el formulario
             document.getElementById('editTarjetaForm').style.display = 'block';
             
             // Ocultar el formulario de agregar si está visible
             document.getElementById('addTarjetaForm').style.display = 'none';
         }
         
         function hideEditTarjetaForm() {
             document.getElementById('editTarjetaForm').style.display = 'none';
         }
        
        // Presupuestos
        function showAddPresupuestoForm() {
            document.getElementById('addPresupuestoForm').style.display = 'block';
            // Establecer mes y año actual por defecto
            const now = new Date();
            const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
            document.getElementById('presupuesto_mes').value = months[now.getMonth()];
            document.getElementById('presupuesto_año').value = now.getFullYear();
        }
        
        function hideAddPresupuestoForm() {
            document.getElementById('addPresupuestoForm').style.display = 'none';
        }
        
        // Recordatorios
        function showAddRecordatorioForm() {
            document.getElementById('addRecordatorioForm').style.display = 'block';
            // Establecer fecha actual por defecto
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('recordatorio_fecha').value = today;
        }
        
        function hideAddRecordatorioForm() {
            document.getElementById('addRecordatorioForm').style.display = 'none';
        }
        
        function showEditRecordatorioForm(id, titulo, descripcion, monto, fecha_vencimiento, tarjeta_id, categoria_id, prioridad) {
            // Por ahora redirigimos a la página principal con parámetros de edición
            window.location.href = '/?edit_recordatorio_id=' + id;
        }
        
        // Inicializar fechas por defecto cuando se carga la página
        document.addEventListener('DOMContentLoaded', function() {
            // Establecer fecha actual en formularios de transacciones
            const today = new Date().toISOString().split('T')[0];
            const fechaInput = document.getElementById('fecha');
            if (fechaInput) {
                fechaInput.value = today;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Página principal con dashboard de finanzas"""
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
    balance = get_balance()
    categorias = get_categories()
    tarjetas = get_tarjetas()
    membresias = get_membresias()
    presupuestos = get_presupuestos()
    recordatorios = get_recordatorios()
    transacciones = get_transactions(filtros)
    dashboard_stats = get_dashboard_stats()
    
    # Calcular total del filtro
    total_filtrado = 0
    filtros_aplicados = None
    if filtros:
        filtros_aplicados = filtros
        for t in transacciones:
            if filtros.get('tipo') == 'ingreso':
                total_filtrado += t['monto']
            elif filtros.get('tipo') == 'gasto':
                total_filtrado += t['monto']
            else:
                total_filtrado += t['monto'] if t['tipo'] == 'ingreso' else -t['monto']
    
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
                                today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """Agregar nueva transacción"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transacciones (descripcion, monto, tipo, categoria_id, tarjeta_id, fecha, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['descripcion'],
            float(request.form['monto']),
            request.form['tipo'],
            request.form['categoria_id'] or None,
            request.form['tarjeta_id'] or None,
            request.form['fecha'],
            request.form['notas'] or None
        ))
        
        conn.commit()
        conn.close()
        
        return redirect('/?success=1')
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/edit_transaction/<int:id>')
def edit_transaction(id):
    """Editar transacción"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transacciones WHERE id = ?', (id,))
    transaction = cursor.fetchone()
    conn.close()
    
    if not transaction:
        return redirect('/?error=Transacción no encontrada')
    
    # Por ahora redirigimos a la página principal con un mensaje
    # En una versión futura podríamos crear un formulario de edición
    return redirect('/?edit_id=' + str(id))

@app.route('/delete_transaction/<int:id>')
def delete_transaction(id):
    """Eliminar transacción"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transacciones WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return redirect('/?deleted=1')
    except Exception as e:
        return redirect('/?error=' + str(e))

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
def add_membresia():
    """Agregar nueva membresía"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO membresias (nombre, plataforma, tipo, monto_mensual, monto_anual, tarjeta_id, fecha_inicio, fecha_renovacion, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['nombre'],
            request.form['plataforma'],
            request.form['tipo'],
            float(request.form['monto_mensual']),
            float(request.form['monto_anual']) if request.form.get('monto_anual') else None,
            request.form['tarjeta_id'] or None,
            request.form['fecha_inicio'],
            request.form['fecha_renovacion'],
            request.form.get('notas')
        ))
        
        conn.commit()
        conn.close()
        
        return redirect('/?success=membresia_agregada')
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/edit_membresia/<int:id>', methods=['GET', 'POST'])
def edit_membresia(id):
    """Editar membresía"""
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE membresias 
                SET nombre=?, plataforma=?, tipo=?, monto_mensual=?, monto_anual=?, 
                    tarjeta_id=?, fecha_inicio=?, fecha_renovacion=?, notas=?
                WHERE id=?
            ''', (
                request.form['nombre'],
                request.form['plataforma'],
                request.form['tipo'],
                float(request.form['monto_mensual']),
                float(request.form['monto_anual']) if request.form.get('monto_anual') else None,
                request.form['tarjeta_id'] or None,
                request.form['fecha_inicio'],
                request.form['fecha_renovacion'],
                request.form.get('notas'),
                id
            ))
            
            conn.commit()
            conn.close()
            
            return redirect('/?success=membresia_editada')
        except Exception as e:
            return redirect('/?error=' + str(e))
    
    # GET: Mostrar formulario de edición
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM membresias WHERE id = ?', (id,))
    membresia = cursor.fetchone()
    conn.close()
    
    if not membresia:
        return redirect('/?error=Membresía no encontrada')
    
    # Por ahora redirigimos a la página principal con un mensaje
    # En una versión futura podríamos crear un formulario de edición
    return redirect('/?edit_membresia_id=' + str(id))

@app.route('/delete_membresia/<int:id>')
def delete_membresia(id):
    """Eliminar membresía"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM membresias WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return redirect('/?success=membresia_eliminada')
    except Exception as e:
        return redirect('/?error=' + str(e))

# ===== RUTAS PARA TARJETAS =====

@app.route('/add_tarjeta', methods=['POST'])
def add_tarjeta():
    """Agregar nueva tarjeta"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tarjetas (nombre, tipo, banco, limite_credito, fecha_vencimiento, color, icono)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['nombre'],
            request.form['tipo'],
            request.form.get('banco'),
            float(request.form['limite_credito']) if request.form.get('limite_credito') else 0,
            request.form.get('fecha_vencimiento'),
            request.form.get('color', '#667eea'),
            request.form.get('icono', '💳')
        ))
        
        conn.commit()
        conn.close()
        
        return redirect('/?success=tarjeta_agregada')
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/edit_tarjeta/<int:id>', methods=['GET', 'POST'])
def edit_tarjeta(id):
    """Editar tarjeta"""
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tarjetas 
                SET nombre=?, tipo=?, banco=?, limite_credito=?, fecha_vencimiento=?, color=?, icono=?
                WHERE id=?
            ''', (
                request.form['nombre'],
                request.form['tipo'],
                request.form.get('banco'),
                float(request.form['limite_credito']) if request.form.get('limite_credito') else 0,
                request.form.get('fecha_vencimiento'),
                request.form.get('color', '#667eea'),
                request.form.get('icono', '💳'),
                id
            ))
            
            conn.commit()
            conn.close()
            
            return redirect('/?success=tarjeta_editada')
        except Exception as e:
            return redirect('/?error=' + str(e))
    
    # GET: Mostrar formulario de edición
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tarjetas WHERE id = ?', (id,))
    tarjeta = cursor.fetchone()
    conn.close()
    
    if not tarjeta:
        return redirect('/?error=Tarjeta no encontrada')
    
    return redirect('/?edit_tarjeta_id=' + str(id))

@app.route('/delete_tarjeta/<int:id>')
def delete_tarjeta(id):
    """Eliminar tarjeta"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tarjetas WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return redirect('/?success=tarjeta_eliminada')
    except Exception as e:
        return redirect('/?error=' + str(e))

# ===== RUTAS PARA PRESUPUESTOS =====

@app.route('/add_presupuesto', methods=['POST'])
def add_presupuesto():
    """Agregar nuevo presupuesto"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO presupuestos (mes, año, categoria_id, monto_planificado)
            VALUES (?, ?, ?, ?)
        ''', (
            request.form['mes'],
            int(request.form['año']),
            request.form['categoria_id'],
            float(request.form['monto_planificado'])
        ))
        
        conn.commit()
        conn.close()
        
        return redirect('/?success=presupuesto_agregado')
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/edit_presupuesto/<int:id>', methods=['GET', 'POST'])
def edit_presupuesto(id):
    """Editar presupuesto"""
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE presupuestos 
                SET mes=?, año=?, categoria_id=?, monto_planificado=?
                WHERE id=?
            ''', (
                request.form['mes'],
                int(request.form['año']),
                request.form['categoria_id'],
                float(request.form['monto_planificado']),
                id
            ))
            
            conn.commit()
            conn.close()
            
            return redirect('/?success=presupuesto_editado')
        except Exception as e:
            return redirect('/?error=' + str(e))
    
    # GET: Mostrar formulario de edición
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM presupuestos WHERE id = ?', (id,))
    presupuesto = cursor.fetchone()
    conn.close()
    
    if not presupuesto:
        return redirect('/?error=Presupuesto no encontrado')
    
    return redirect('/?edit_presupuesto_id=' + str(id))

@app.route('/delete_presupuesto/<int:id>')
def delete_presupuesto(id):
    """Eliminar presupuesto"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM presupuestos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return redirect('/?success=presupuesto_eliminado')
    except Exception as e:
        return redirect('/?error=' + str(e))

# ===== RUTAS PARA RECORDATORIOS =====

@app.route('/add_recordatorio', methods=['POST'])
def add_recordatorio():
    """Agregar nuevo recordatorio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recordatorios (titulo, descripcion, monto, fecha_vencimiento, tarjeta_id, categoria_id, prioridad)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['titulo'],
            request.form.get('descripcion'),
            float(request.form['monto']),
            request.form['fecha_vencimiento'],
            request.form['tarjeta_id'] or None,
            request.form['categoria_id'] or None,
            request.form.get('prioridad', 'normal')
        ))
        
        conn.commit()
        conn.close()
        
        return redirect('/?success=recordatorio_agregado')
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/edit_recordatorio/<int:id>', methods=['GET', 'POST'])
def edit_recordatorio(id):
    """Editar recordatorio"""
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE recordatorios 
                SET titulo=?, descripcion=?, monto=?, fecha_vencimiento=?, 
                    tarjeta_id=?, categoria_id=?, prioridad=?
                WHERE id=?
            ''', (
                request.form['titulo'],
                request.form.get('descripcion'),
                float(request.form['monto']),
                request.form['fecha_vencimiento'],
                request.form['tarjeta_id'] or None,
                request.form['categoria_id'] or None,
                request.form.get('prioridad', 'normal'),
                id
            ))
            
            conn.commit()
            conn.close()
            
            return redirect('/?success=recordatorio_editado')
        except Exception as e:
            return redirect('/?error=' + str(e))
    
    # GET: Mostrar formulario de edición
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recordatorios WHERE id = ?', (id,))
    recordatorio = cursor.fetchone()
    conn.close()
    
    if not recordatorio:
        return redirect('/?error=Recordatorio no encontrado')
    
    return redirect('/?edit_recordatorio_id=' + str(id))

@app.route('/delete_recordatorio/<int:id>')
def delete_recordatorio(id):
    """Eliminar recordatorio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM recordatorios WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return redirect('/?success=recordatorio_eliminado')
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/completar_recordatorio/<int:id>')
def completar_recordatorio(id):
    """Marcar recordatorio como completado"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE recordatorios SET estado = "completado" WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return redirect('/?success=recordatorio_completado')
    except Exception as e:
        return redirect('/?error=' + str(e))

# ===== RUTAS PARA CATEGORÍAS =====

@app.route('/add_categoria', methods=['POST'])
def add_categoria():
    """Agregar nueva categoría"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO categorias (nombre, tipo, color, icono, presupuesto_mensual)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            request.form['nombre'],
            request.form['tipo'],
            request.form.get('color', '#667eea'),
            request.form.get('icono', '💰'),
            float(request.form.get('presupuesto_mensual', 0))
        ))
        
        conn.commit()
        conn.close()
        
        return redirect('/?success=categoria_agregada')
    except Exception as e:
        return redirect('/?error=' + str(e))

@app.route('/edit_categoria/<int:id>', methods=['GET', 'POST'])
def edit_categoria(id):
    """Editar categoría"""
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE categorias 
                SET nombre=?, tipo=?, color=?, icono=?, presupuesto_mensual=?
                WHERE id=?
            ''', (
                request.form['nombre'],
                request.form['tipo'],
                request.form.get('color', '#667eea'),
                request.form.get('icono', '💰'),
                float(request.form.get('presupuesto_mensual', 0)),
                id
            ))
            
            conn.commit()
            conn.close()
            
            return redirect('/?success=categoria_editada')
        except Exception as e:
            return redirect('/?error=' + str(e))
    
    # GET: Mostrar formulario de edición
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias WHERE id = ?', (id,))
    categoria = cursor.fetchone()
    conn.close()
    
    if not categoria:
        return redirect('/?error=Categoría no encontrada')
    
    return redirect('/?edit_categoria_id=' + str(id))

@app.route('/delete_categoria/<int:id>')
def delete_categoria(id):
    """Eliminar categoría"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM categorias WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return redirect('/?success=categoria_eliminada')
    except Exception as e:
        return redirect('/?error=' + str(e))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Iniciando aplicación de finanzas en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
