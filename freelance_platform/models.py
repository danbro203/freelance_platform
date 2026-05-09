from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')
    orders = db.relationship('Order', backref='client', lazy=True, foreign_keys='Order.client_id')
    responses = db.relationship('Response', backref='worker', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(300))
    status = db.Column(db.String(50), default='Открыт')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responses = db.relationship('Response', backref='order', lazy=True, cascade='all, delete-orphan')

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='waiting')