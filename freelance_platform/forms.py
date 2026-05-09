from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    role = RadioField('Я:', choices=[('customer', 'Заказчик'), ('worker', 'Работник')], default='customer')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Это имя уже занято')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Этот email уже используется')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class OrderForm(FlaskForm):
    title = StringField('Название заказа', validators=[DataRequired()])
    description = TextAreaField('Описание заказа', validators=[DataRequired()])
    file = FileField('Прикрепить файл', validators=[FileAllowed(['pdf', 'doc', 'docx', 'txt', 'zip'])])
    submit = SubmitField('Создать заказ')

class ResponseForm(FlaskForm):
    message = TextAreaField('Ваше предложение', validators=[DataRequired()])
    price = IntegerField('Цена (₽)', validators=[Optional()])
    submit = SubmitField('Откликнуться')