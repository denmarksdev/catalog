# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db

# PASSWORD HASH
from passlib.apps import custom_app_context as pwd_context


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    picture = db.Column(db.String(250))
    username = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
