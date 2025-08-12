# This file was created to run the application on Railway using gunicorn.
# Read more about it here: https://devcenter.heroku.com/articles/python-gunicorn

from app import app

# Initialize database tables
with app.app_context():
    from api.models import db
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Database setup error: {e}")

if __name__ == "__main__":
    app.run()
