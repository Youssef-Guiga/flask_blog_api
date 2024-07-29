from config import app, db
from models import User, Post

with app.app_context():
    db.create_all()
    print("Database created successfully!")
