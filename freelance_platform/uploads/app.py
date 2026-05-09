from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Модели
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_orders = db.relationship('Order', backref='client', lazy=True)
    responses = db.relationship('Response', backref='worker', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.worker_id', backref='reviewed_worker', lazy=True)
    reviews_given = db.relationship('Review', foreign_keys='Review.customer_id', backref='reviewer', lazy=True)
    
    def average_rating(self):
        if not self.reviews_received:
            return 0
        return sum(r.rating for r in self.reviews_received) / len(self.reviews_received)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    file_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responses = db.relationship('Response', backref='order', lazy=True)
    reviews = db.relationship('Review', backref='order', lazy=True)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer)
    status = db.Column(db.String(20), default='waiting')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Формы
class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    role = RadioField('Роль', choices=[('customer', 'Заказчик'), ('worker', 'Исполнитель')], default='customer')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя уже занято')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже используется')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class OrderForm(FlaskForm):
    title = StringField('Название заказа', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    file = FileField('Прикрепить файл', validators=[FileAllowed(['pdf', 'doc', 'docx', 'txt', 'zip', 'py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'json', 'xml'])])
    submit = SubmitField('Создать заказ')

class ResponseForm(FlaskForm):
    message = TextAreaField('Сообщение', validators=[DataRequired()])
    price = IntegerField('Предложенная цена (руб)')
    submit = SubmitField('Отправить отклик')

class ReviewForm(FlaskForm):
    rating = RadioField('Оценка', choices=[(5, '⭐⭐⭐⭐⭐ Отлично'), (4, '⭐⭐⭐⭐ Хорошо'), (3, '⭐⭐⭐ Нормально'), (2, '⭐⭐ Плохо'), (1, '⭐ Ужасно')], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Отзыв')
    submit = SubmitField('Оставить отзыв')

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Теперь можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный email или пароль', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'customer':
        orders = Order.query.filter_by(client_id=current_user.id).all()
        return render_template('dashboard_customer.html', orders=orders)
    else:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        
        query = Order.query.filter_by(status='open')
        if search:
            query = query.filter(Order.title.ilike(f'%{search}%'))
        
        pagination = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=6, error_out=False
        )
        
        responses = Response.query.filter_by(worker_id=current_user.id).all()
        return render_template('dashboard_worker.html', 
                             orders=pagination.items,
                             pagination=pagination,
                             responses=responses,
                             search=search)

@app.route('/orders')
def orders():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status = request.args.get('status', '', type=str)
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    else:
        query = query.filter_by(status='open')
    
    if search:
        query = query.filter(Order.title.ilike(f'%{search}%'))
    
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    
    return render_template('orders.html', 
                         orders=pagination.items,
                         pagination=pagination,
                         search=search,
                         status=status)

@app.route('/create_order', methods=['GET', 'POST'])
@login_required
def create_order():
    if current_user.role != 'customer':
        flash('Только заказчики могут создавать заказы', 'danger')
        return redirect(url_for('dashboard'))
    
    form = OrderForm()
    if form.validate_on_submit():
        file_path = None
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.file.data.save(file_path)
        
        order = Order(
            title=form.title.data,
            description=form.description.data,
            file_path=file_path,
            client_id=current_user.id
        )
        db.session.add(order)
        db.session.commit()
        flash('Заказ успешно создан!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_order.html', form=form)

@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    if current_user.is_authenticated and current_user.role == 'worker':
        form = ResponseForm()
        if form.validate_on_submit():
            existing = Response.query.filter_by(order_id=order_id, worker_id=current_user.id).first()
            if existing:
                flash('Вы уже откликнулись на этот заказ', 'warning')
                return redirect(url_for('order_detail', order_id=order_id))
            
            response = Response(
                message=form.message.data,
                price=form.price.data,
                order_id=order_id,
                worker_id=current_user.id
            )
            db.session.add(response)
            db.session.commit()
            flash('Отклик отправлен!', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('order_detail_worker.html', order=order, form=form)
    
    elif current_user.is_authenticated and current_user.role == 'customer':
        responses = Response.query.filter_by(order_id=order_id).all()
        return render_template('order_detail_customer.html', order=order, responses=responses)
    
    else:
        flash('Войдите, чтобы просмотреть детали заказа', 'info')
        return redirect(url_for('login'))

@app.route('/accept_response/<int:response_id>')
@login_required
def accept_response(response_id):
    response = Response.query.get_or_404(response_id)
    
    if response.order.client_id != current_user.id:
        flash('У вас нет прав на это действие', 'danger')
        return redirect(url_for('dashboard'))
    
    response.status = 'accepted'
    response.order.status = 'in_progress'
    db.session.commit()
    flash('Отклик принят!', 'success')
    return redirect(url_for('order_detail', order_id=response.order_id))

@app.route('/complete_order/<int:order_id>')
@login_required
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.client_id != current_user.id:
        flash('У вас нет прав на это действие', 'danger')
        return redirect(url_for('dashboard'))
    
    order.status = 'completed'
    db.session.commit()
    flash('Заказ завершён!', 'success')
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/add_review/<int:order_id>', methods=['GET', 'POST'])
@login_required
def add_review(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.client_id != current_user.id:
        flash('Только заказчик может оставить отзыв', 'danger')
        return redirect(url_for('dashboard'))
    
    if order.status != 'completed':
        flash('Можно оставить отзыв только на завершённый заказ', 'warning')
        return redirect(url_for('order_detail', order_id=order_id))
    
    accepted_response = Response.query.filter_by(order_id=order_id, status='accepted').first()
    if not accepted_response:
        flash('Нет принятого исполнителя для отзыва', 'warning')
        return redirect(url_for('order_detail', order_id=order_id))
    
    existing_review = Review.query.filter_by(order_id=order_id).first()
    if existing_review:
        flash('Вы уже оставили отзыв на этот заказ', 'info')
        return redirect(url_for('order_detail', order_id=order_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            order_id=order_id,
            worker_id=accepted_response.worker_id,
            customer_id=current_user.id
        )
        db.session.add(review)
        db.session.commit()
        flash('Отзыв успешно добавлен!', 'success')
        return redirect(url_for('worker_profile', user_id=accepted_response.worker_id))
    
    return render_template('add_review.html', form=form, order=order, worker=accepted_response.worker)

@app.route('/worker/<int:user_id>')
def worker_profile(user_id):
    worker = User.query.get_or_404(user_id)
    
    if worker.role != 'worker':
        flash('Это не профиль работника', 'warning')
        return redirect(url_for('index'))
    
    reviews = Review.query.filter_by(worker_id=user_id).order_by(Review.created_at.desc()).all()
    avg_rating = worker.average_rating()
    
    return render_template('worker_profile.html', worker=worker, reviews=reviews, avg_rating=avg_rating)

@app.route('/download/<int:order_id>')
@login_required
def download_file(order_id):
    order = Order.query.get_or_404(order_id)
    
    if current_user.id != order.client_id and current_user.role != 'worker':
        flash('Нет доступа к файлу', 'danger')
        return redirect(url_for('index'))
    
    if not order.file_path or not os.path.exists(order.file_path):
        flash('Файл не найден', 'warning')
        return redirect(url_for('order_detail', order_id=order_id))
    
    return send_file(order.file_path, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)