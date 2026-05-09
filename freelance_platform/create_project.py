import os

print('🚀 Создаю проект...')

# Папки
for folder in ['templates', 'static/css', 'static/uploads', 'static/img']:
    os.makedirs(folder, exist_ok=True)

# app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write('''from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Order
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Успешно!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вход выполнен!', 'success')
            return redirect(url_for('dashboard'))
        flash('Ошибка', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(client_id=current_user.id).all()
    return render_template('dashboard.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
''')

# models.py
with open('models.py', 'w', encoding='utf-8') as f:
    f.write('''from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    orders = db.relationship('Order', backref='client', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(300))
    status = db.Column(db.String(50), default='Новый')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
''')

# forms.py
with open('forms.py', 'w', encoding='utf-8') as f:
    f.write('''from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Повтор', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Занято')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Занято')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
''')

# requirements.txt
with open('requirements.txt', 'w') as f:
    f.write('Flask==3.0.0\\nFlask-SQLAlchemy==3.1.1\\nFlask-Login==0.6.3\\nWerkzeug==3.0.1\\nFlask-WTF==1.2.1\\nWTForms==3.1.1\\nemail-validator==2.1.0\\n')

# Шаблоны
with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write('''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{% block title %}Биржа{% endblock %}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body><nav class="navbar navbar-dark bg-dark"><div class="container">
<a class="navbar-brand" href="/">Биржа</a><div class="navbar-nav ms-auto">
<a class="nav-link" href="/">Главная</a>
{% if current_user.is_authenticated %}<a class="nav-link" href="/dashboard">Кабинет</a><a class="nav-link" href="/logout">Выход</a>
{% else %}<a class="nav-link" href="/login">Вход</a><a class="nav-link" href="/register">Регистрация</a>{% endif %}
</div></div></nav><div class="container mt-4">
{% with messages = get_flashed_messages(with_categories=true) %}{% if messages %}
{% for cat, msg in messages %}<div class="alert alert-{{cat}}">{{msg}}</div>{% endfor %}{% endif %}{% endwith %}
{% block content %}{% endblock %}</div></body></html>''')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write('{% extends "base.html" %}{% block content %}<div class="text-center py-5"><h1>Биржа фриланса</h1><a href="/register" class="btn btn-primary">Начать</a></div>{% endblock %}')

with open('templates/register.html', 'w', encoding='utf-8') as f:
    f.write('{% extends "base.html" %}{% block content %}<div class="col-md-6 mx-auto"><div class="card"><div class="card-body"><h3>Регистрация</h3><form method="POST">{{form.hidden_tag()}}<div class="mb-3">{{form.username.label(class="form-label")}}{{form.username(class="form-control")}}</div><div class="mb-3">{{form.email.label(class="form-label")}}{{form.email(class="form-control")}}</div><div class="mb-3">{{form.password.label(class="form-label")}}{{form.password(class="form-control")}}</div><div class="mb-3">{{form.confirm_password.label(class="form-label")}}{{form.confirm_password(class="form-control")}}</div>{{form.submit(class="btn btn-primary")}}</form></div></div></div>{% endblock %}')

with open('templates/login.html', 'w', encoding='utf-8') as f:
    f.write('{% extends "base.html" %}{% block content %}<div class="col-md-6 mx-auto"><div class="card"><div class="card-body"><h3>Вход</h3><form method="POST">{{form.hidden_tag()}}<div class="mb-3">{{form.email.label(class="form-label")}}{{form.email(class="form-control")}}</div><div class="mb-3">{{form.password.label(class="form-label")}}{{form.password(class="form-control")}}</div>{{form.submit(class="btn btn-success")}}</form></div></div></div>{% endblock %}')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write('{% extends "base.html" %}{% block content %}<h2>Привет, {{current_user.username}}!</h2><hr><h4>Заказы</h4>{% if orders %}<table class="table"><tr><th>ID</th><th>Название</th><th>Статус</th></tr>{% for o in orders %}<tr><td>{{o.id}}</td><td>{{o.title}}</td><td>{{o.status}}</td></tr>{% endfor %}</table>{% else %}<p>Нет заказов</p>{% endif %}{% endblock %}')

print('✅ Все файлы созданы!')
print('Теперь: pip install -r requirements.txt')
print('Затем: python app.py')