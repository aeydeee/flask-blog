# init_db.py
from app import create_app, db

print("Creating app...")
app = create_app()

print("Pushing app context...")
with app.app_context():
    print("Creating all database tables...")
    db.create_all()
    print("Database tables created successfully.")

print("Initialization complete.")
