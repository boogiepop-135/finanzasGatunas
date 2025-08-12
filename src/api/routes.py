"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Category, Transaction, RecurringPayment, TransactionType, RecurrenceFrequency
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import func, extract

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "¡Miau! Bienvenido a Finanzas Gatunas 🐱💰"
    }
    return jsonify(response_body), 200

# ================= CATEGORÍAS =================
@api.route('/categories', methods=['GET'])
def get_categories():
    try:
        user_id = request.args.get('user_id', 1)  # Por simplicidad, usamos user_id = 1
        categories = Category.query.filter_by(user_id=user_id).all()
        return jsonify([category.serialize() for category in categories]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/categories', methods=['POST'])
def create_category():
    try:
        data = request.get_json()
        category = Category(
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#FF69B4'),
            icon=data.get('icon', '🐱'),
            user_id=data.get('user_id', 1)
        )
        db.session.add(category)
        db.session.commit()
        return jsonify(category.serialize()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.color = data.get('color', category.color)
        category.icon = data.get('icon', category.icon)
        
        db.session.commit()
        return jsonify(category.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Categoría eliminada con éxito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= TRANSACCIONES =================
@api.route('/transactions', methods=['GET'])
def get_transactions():
    try:
        user_id = request.args.get('user_id', 1)
        month = request.args.get('month')
        year = request.args.get('year')
        
        query = Transaction.query.filter_by(user_id=user_id)
        
        if month and year:
            query = query.filter(
                extract('month', Transaction.transaction_date) == int(month),
                extract('year', Transaction.transaction_date) == int(year)
            )
        
        transactions = query.order_by(Transaction.transaction_date.desc()).all()
        return jsonify([transaction.serialize() for transaction in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        transaction = Transaction(
            amount=float(data['amount']),
            description=data['description'],
            transaction_type=TransactionType(data['transaction_type']),
            transaction_date=datetime.fromisoformat(data.get('transaction_date', datetime.now().isoformat())),
            user_id=data.get('user_id', 1),
            category_id=data['category_id']
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify(transaction.serialize()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        data = request.get_json()
        
        transaction.amount = float(data.get('amount', transaction.amount))
        transaction.description = data.get('description', transaction.description)
        if 'transaction_type' in data:
            transaction.transaction_type = TransactionType(data['transaction_type'])
        if 'transaction_date' in data:
            transaction.transaction_date = datetime.fromisoformat(data['transaction_date'])
        transaction.category_id = data.get('category_id', transaction.category_id)
        
        db.session.commit()
        return jsonify(transaction.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transacción eliminada con éxito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= PAGOS RECURRENTES =================
@api.route('/recurring-payments', methods=['GET'])
def get_recurring_payments():
    try:
        user_id = request.args.get('user_id', 1)
        payments = RecurringPayment.query.filter_by(user_id=user_id).all()
        return jsonify([payment.serialize() for payment in payments]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/recurring-payments', methods=['POST'])
def create_recurring_payment():
    try:
        data = request.get_json()
        payment = RecurringPayment(
            name=data['name'],
            amount=float(data['amount']),
            description=data.get('description', ''),
            frequency=RecurrenceFrequency(data['frequency']),
            next_payment_date=datetime.fromisoformat(data['next_payment_date']),
            user_id=data.get('user_id', 1),
            category_id=data['category_id']
        )
        db.session.add(payment)
        db.session.commit()
        return jsonify(payment.serialize()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/recurring-payments/<int:payment_id>', methods=['PUT'])
def update_recurring_payment(payment_id):
    try:
        payment = RecurringPayment.query.get_or_404(payment_id)
        data = request.get_json()
        
        payment.name = data.get('name', payment.name)
        payment.amount = float(data.get('amount', payment.amount))
        payment.description = data.get('description', payment.description)
        if 'frequency' in data:
            payment.frequency = RecurrenceFrequency(data['frequency'])
        if 'next_payment_date' in data:
            payment.next_payment_date = datetime.fromisoformat(data['next_payment_date'])
        payment.is_active = data.get('is_active', payment.is_active)
        payment.category_id = data.get('category_id', payment.category_id)
        
        db.session.commit()
        return jsonify(payment.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/recurring-payments/<int:payment_id>', methods=['DELETE'])
def delete_recurring_payment(payment_id):
    try:
        payment = RecurringPayment.query.get_or_404(payment_id)
        db.session.delete(payment)
        db.session.commit()
        return jsonify({"message": "Pago recurrente eliminado con éxito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= ESTADÍSTICAS Y REPORTES =================
@api.route('/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    try:
        user_id = request.args.get('user_id', 1)
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        
        # Ingresos del mes
        income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.INCOME,
            extract('month', Transaction.transaction_date) == int(month),
            extract('year', Transaction.transaction_date) == int(year)
        ).scalar() or 0
        
        # Gastos del mes
        expenses = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            extract('month', Transaction.transaction_date) == int(month),
            extract('year', Transaction.transaction_date) == int(year)
        ).scalar() or 0
        
        # Balance
        balance = income - expenses
        
        # Gastos por categoría
        expenses_by_category = db.session.query(
            Category.name,
            Category.color,
            Category.icon,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            extract('month', Transaction.transaction_date) == int(month),
            extract('year', Transaction.transaction_date) == int(year)
        ).group_by(Category.id).all()
        
        return jsonify({
            "income": float(income),
            "expenses": float(expenses),
            "balance": float(balance),
            "expenses_by_category": [
                {
                    "name": item.name,
                    "color": item.color,
                    "icon": item.icon,
                    "amount": float(item.total)
                }
                for item in expenses_by_category
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/dashboard/monthly-trend', methods=['GET'])
def get_monthly_trend():
    try:
        user_id = request.args.get('user_id', 1)
        year = request.args.get('year', datetime.now().year)
        
        # Obtener datos por mes
        monthly_data = []
        for month in range(1, 13):
            income = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.INCOME,
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == int(year)
            ).scalar() or 0
            
            expenses = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.EXPENSE,
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == int(year)
            ).scalar() or 0
            
            monthly_data.append({
                "month": month,
                "income": float(income),
                "expenses": float(expenses),
                "balance": float(income - expenses)
            })
        
        return jsonify(monthly_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
