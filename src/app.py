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
    
    # Tabla de categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL,
            color TEXT DEFAULT '#667eea',
            icono TEXT DEFAULT '💰'
        )
    ''')
    
    # Tabla de transacciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            tipo TEXT NOT NULL,
            categoria_id INTEGER,
            fecha DATE NOT NULL,
            notas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
    ''')
    
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
        ('Otros', 'gasto', '#9E9E9E', '📦')
    ]
    
    for cat in categorias_default:
        try:
            cursor.execute('INSERT INTO categorias (nombre, tipo, color, icono) VALUES (?, ?, ?, ?)', cat)
        except sqlite3.IntegrityError:
            pass  # La categoría ya existe
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

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
    
    balance = total_ingresos - total_gastos
    
    conn.close()
    return {
        'ingresos': total_ingresos,
        'gastos': total_gastos,
        'balance': balance
    }

def get_transactions(filtros=None):
    """Obtener transacciones con filtros"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT t.*, c.nombre as categoria_nombre, c.color, c.icono
        FROM transacciones t
        LEFT JOIN categorias c ON t.categoria_id = c.id
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

# HTML template principal
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐱 Finanzas Gatunas - Control de Finanzas del Hogar</title>
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
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
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
        
        .controls-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .controls-section h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5rem;
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
        
        .filters-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .filters-section h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5rem;
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
        
        .transactions-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .transactions-section h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5rem;
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
        
        .charts-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .charts-section h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5rem;
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
        
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .transactions-table {
                font-size: 14px;
            }
            
            .transactions-table th,
            .transactions-table td {
                padding: 10px 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐱 Finanzas Gatunas</h1>
            <p>Control completo de finanzas del hogar</p>
        </div>
        
        <!-- Estadísticas principales -->
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
        </div>
        
        <!-- Controles para agregar transacciones -->
        <div class="controls-section">
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
                                {% if cat.tipo == 'ingreso' %}
                                    <option value="{{ cat.id }}" data-tipo="{{ cat.tipo }}">{{ cat.icono }} {{ cat.nombre }}</option>
                                {% endif %}
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="fecha">Fecha *</label>
                        <input type="date" id="fecha" name="fecha" value="{{ today }}" required>
                    </div>
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
        
        <!-- Filtros -->
        <div class="filters-section">
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
                        <label for="filter_fecha_inicio">Fecha Inicio</label>
                        <input type="date" id="filter_fecha_inicio" name="filter_fecha_inicio">
                    </div>
                    <div class="form-group">
                        <label for="filter_fecha_fin">Fecha Fin</label>
                        <input type="date" id="filter_fecha_fin" name="filter_fecha_fin">
                    </div>
                </div>
                <div class="form-row">
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
        
        <!-- Transacciones -->
        <div class="transactions-section">
            <h3>
                <i class="fas fa-list"></i> Transacciones
                <div style="float: right;">
                    <a href="/export_csv" class="btn btn-success">
                        <i class="fas fa-download"></i> Exportar CSV
                    </a>
                    <a href="/export_json" class="btn btn-warning">
                        <i class="fas fa-code"></i> Exportar JSON
                    </a>
                </div>
            </h3>
            
            {% if transacciones %}
            <table class="transactions-table">
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Descripción</th>
                        <th>Categoría</th>
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
        
        <!-- Gráficas -->
        <div class="charts-section">
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
    
    <script>
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
    if request.args.get('filter_fecha_inicio'):
        filtros['fecha_inicio'] = request.args.get('filter_fecha_inicio')
    if request.args.get('filter_fecha_fin'):
        filtros['fecha_fin'] = request.args.get('filter_fecha_fin')
    if request.args.get('filter_descripcion'):
        filtros['descripcion'] = request.args.get('filter_descripcion')
    
    # Obtener datos
    balance = get_balance()
    categorias = get_categories()
    transacciones = get_transactions(filtros)
    
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
                                transacciones=transacciones,
                                filtros_aplicados=filtros_aplicados,
                                total_filtrado=total_filtrado,
                                chart_data=chart_data,
                                today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """Agregar nueva transacción"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transacciones (descripcion, monto, tipo, categoria_id, fecha, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            request.form['descripcion'],
            float(request.form['monto']),
            request.form['tipo'],
            request.form['categoria_id'] or None,
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
        writer.writerow(['Fecha', 'Descripción', 'Categoría', 'Monto', 'Tipo', 'Notas'])
        
        # Datos
        for t in transacciones:
            writer.writerow([
                t['fecha'],
                t['descripcion'],
                t['categoria_nombre'] or 'Sin categoría',
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

if __name__ == '__main__':
    # Inicializar base de datos
    init_db()
    
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Iniciando aplicación de finanzas en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
