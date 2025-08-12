
import click
from api.models import db, User, Category, Transaction, RecurringPayment, TransactionType, RecurrenceFrequency
from datetime import datetime, timedelta
import random

"""
In this file, you can add as many commands as you want using the @app.cli.command decorator
Flask commands are usefull to run cronjobs or tasks outside of the API but sill in integration 
with youy database, for example: Import the price of bitcoin every night as 12am
"""
def setup_commands(app):
    
    """ 
    This is an example command "insert-test-users" that you can run from the command line
    by typing: $ flask insert-test-users 5
    Note: 5 is the number of users to add
    """
    @app.cli.command("insert-test-users") # name of our command
    @click.argument("count") # argument of out command
    def insert_test_users(count):
        print("Creating test users")
        for x in range(1, int(count) + 1):
            user = User()
            user.email = "test_user" + str(x) + "@test.com"
            user.password = "123456"
            user.is_active = True
            user.name = f"Usuario {x}"
            db.session.add(user)
            db.session.commit()
            print("User: ", user.email, " created.")

        print("All test users created")

    @app.cli.command("insert-test-data")
    def insert_test_data():
        print("🐱 Creando datos de ejemplo para Finanzas Gatunas...")
        
        # Crear usuario de prueba si no existe
        user = User.query.filter_by(email="demo@finanzasgatunas.com").first()
        if not user:
            user = User(
                email="demo@finanzasgatunas.com",
                password="123456",
                is_active=True,
                name="Usuario Demo"
            )
            db.session.add(user)
            db.session.commit()
            print("✅ Usuario demo creado")
        
        # Crear categorías
        categories_data = [
            {"name": "Alimentación", "description": "Comida y bebidas", "color": "#FF69B4", "icon": "🍕"},
            {"name": "Transporte", "description": "Gasolina, transporte público", "color": "#87CEEB", "icon": "🚗"},
            {"name": "Hogar", "description": "Servicios públicos, alquiler", "color": "#98FB98", "icon": "🏠"},
            {"name": "Entretenimiento", "description": "Cine, juegos, diversión", "color": "#DDA0DD", "icon": "🎮"},
            {"name": "Salud", "description": "Médico, medicinas", "color": "#FFB6C1", "icon": "💊"},
            {"name": "Compras", "description": "Ropa, accesorios", "color": "#F0E68C", "icon": "🛒"},
            {"name": "Ingresos Salario", "description": "Salario mensual", "color": "#90EE90", "icon": "💰"},
            {"name": "Ingresos Extra", "description": "Trabajos extra, bonos", "color": "#98FB98", "icon": "💎"},
            {"name": "Educación", "description": "Cursos, libros", "color": "#FFA07A", "icon": "📚"},
            {"name": "Mascotas", "description": "Comida y cuidado de gatos", "color": "#FFE4E1", "icon": "🐱"}
        ]
        
        categories = []
        for cat_data in categories_data:
            existing_cat = Category.query.filter_by(name=cat_data["name"], user_id=user.id).first()
            if not existing_cat:
                category = Category(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    color=cat_data["color"],
                    icon=cat_data["icon"],
                    user_id=user.id
                )
                db.session.add(category)
                categories.append(category)
        
        db.session.commit()
        print("✅ Categorías creadas")
        
        # Obtener todas las categorías
        all_categories = Category.query.filter_by(user_id=user.id).all()
        income_categories = [c for c in all_categories if "Ingresos" in c.name]
        expense_categories = [c for c in all_categories if "Ingresos" not in c.name]
        
        # Crear transacciones de ejemplo para los últimos 6 meses
        print("💰 Creando transacciones de ejemplo...")
        
        today = datetime.now()
        for month_offset in range(6):
            month_date = today - timedelta(days=30 * month_offset)
            
            # Ingresos mensuales
            for income_cat in income_categories:
                amount = random.randint(2500000, 4000000) if "Salario" in income_cat.name else random.randint(200000, 800000)
                transaction = Transaction(
                    amount=amount,
                    description=f"Ingreso de {income_cat.name.lower()}",
                    transaction_type=TransactionType.INCOME,
                    transaction_date=month_date.replace(day=random.randint(1, 28)),
                    user_id=user.id,
                    category_id=income_cat.id
                )
                db.session.add(transaction)
            
            # Gastos mensuales
            expense_amounts = {
                "Alimentación": random.randint(400000, 800000),
                "Transporte": random.randint(150000, 300000),
                "Hogar": random.randint(300000, 600000),
                "Entretenimiento": random.randint(100000, 300000),
                "Salud": random.randint(50000, 200000),
                "Compras": random.randint(100000, 400000),
                "Educación": random.randint(50000, 150000),
                "Mascotas": random.randint(80000, 150000)
            }
            
            for expense_cat in expense_categories:
                base_amount = expense_amounts.get(expense_cat.name, 100000)
                # Crear varias transacciones por categoría por mes
                num_transactions = random.randint(2, 6)
                
                for i in range(num_transactions):
                    amount = base_amount // num_transactions + random.randint(-50000, 50000)
                    if amount > 0:
                        transaction = Transaction(
                            amount=amount,
                            description=f"Gasto en {expense_cat.name.lower()} - {i+1}",
                            transaction_type=TransactionType.EXPENSE,
                            transaction_date=month_date.replace(day=random.randint(1, 28)),
                            user_id=user.id,
                            category_id=expense_cat.id
                        )
                        db.session.add(transaction)
        
        db.session.commit()
        print("✅ Transacciones de ejemplo creadas")
        
        # Crear pagos recurrentes
        print("🔄 Creando pagos recurrentes...")
        
        recurring_payments_data = [
            {
                "name": "Netflix",
                "amount": 17000,
                "description": "Suscripción mensual de entretenimiento",
                "frequency": RecurrenceFrequency.MONTHLY,
                "category": "Entretenimiento"
            },
            {
                "name": "Spotify",
                "amount": 15000,
                "description": "Música ilimitada",
                "frequency": RecurrenceFrequency.MONTHLY,
                "category": "Entretenimiento"
            },
            {
                "name": "Internet",
                "amount": 80000,
                "description": "Servicio de internet fibra óptica",
                "frequency": RecurrenceFrequency.MONTHLY,
                "category": "Hogar"
            },
            {
                "name": "Gimnasio",
                "amount": 120000,
                "description": "Membresía mensual del gimnasio",
                "frequency": RecurrenceFrequency.MONTHLY,
                "category": "Salud"
            },
            {
                "name": "Seguro de Vida",
                "amount": 85000,
                "description": "Seguro de vida anual",
                "frequency": RecurrenceFrequency.YEARLY,
                "category": "Salud"
            },
            {
                "name": "Veterinario",
                "amount": 150000,
                "description": "Revisión veterinaria de los gatos",
                "frequency": RecurrenceFrequency.MONTHLY,
                "category": "Mascotas"
            }
        ]
        
        for payment_data in recurring_payments_data:
            category = next((c for c in all_categories if c.name == payment_data["category"]), expense_categories[0])
            
            # Calcular próxima fecha de pago
            if payment_data["frequency"] == RecurrenceFrequency.MONTHLY:
                next_payment = today.replace(day=random.randint(1, 28))
            elif payment_data["frequency"] == RecurrenceFrequency.YEARLY:
                next_payment = today + timedelta(days=random.randint(30, 365))
            else:
                next_payment = today + timedelta(days=random.randint(1, 30))
            
            existing_payment = RecurringPayment.query.filter_by(name=payment_data["name"], user_id=user.id).first()
            if not existing_payment:
                recurring_payment = RecurringPayment(
                    name=payment_data["name"],
                    amount=payment_data["amount"],
                    description=payment_data["description"],
                    frequency=payment_data["frequency"],
                    next_payment_date=next_payment,
                    user_id=user.id,
                    category_id=category.id,
                    is_active=True
                )
                db.session.add(recurring_payment)
        
        db.session.commit()
        print("✅ Pagos recurrentes creados")
        
        print("🎉 ¡Datos de ejemplo creados exitosamente!")
        print("📧 Email: demo@finanzasgatunas.com")
        print("🔑 Password: 123456")
        print("🐱 ¡Disfruta de Finanzas Gatunas!")