import time
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table("users"):
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully")
    else:
        print("Tables already exist")
