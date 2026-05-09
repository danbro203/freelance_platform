import os
import shutil

# Удаляем старые templates
if os.path.exists('templates'):
    shutil.rmtree('templates')

os.makedirs('templates', exist_ok=True)

templates = {
    'base.html': '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Биржа фриланса</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<div class="container">
<a class="navbar-brand" href="/">Биржа фриланса</a>
<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
<span class="navbar-toggler-icon"></span>
</button>
<div class="collapse navbar-collapse" id="navbarNav">
<ul class="navbar-nav ms-auto">
<li class="nav-item"><a class="nav-link" href="/">Главная</a></li>
<li class="nav-item"><a class="nav-link" href="/orders">Заказы</a></li>
{% if current_user.is_authenticated %}
<li class="nav-item"><a class="nav-link" href="/dashboard">Кабинет</a></li>
<li class="nav-item"><a class="nav-link" href="/logout">Выход</a></li>
{% else %}
<li class="nav-item"><a class="nav-link" href="/login">Вход</a></li>
<li class="nav-item"><a class="nav-link" href="/register">Регистрация</a></li>
{% endif %}
</ul>
</div>
</div>
</nav>
<div class="container mt-4">
{% with messages = get_flashed_messages(with_categories=true) %}
{% if messages %}
{% for category, message in messages %}
<div class="alert alert-{{category}} alert-dismissible fade show" role="alert">
{{message}}
<button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
{% endfor %}
{% endif %}
{% endwith %}
{% block content %}{% endblock %}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'index.html': '''{% extends "base.html" %}
{% block content %}
<div class="jumbotron text-center py-5">
<h1 class="display-4">Биржа фриланса</h1>
<p class="lead">Закажите разработку или найдите интересные проекты</p>
<hr class="my-4">
<p>Присоединяйтесь к нашему сообществу!</p>
<a class="btn btn-primary btn-lg" href="/register" role="button">Начать работу</a>
<a class="btn btn-outline-secondary btn-lg" href="/orders" role="button">Посмотреть заказы</a>
</div>
{% endblock %}''',

    'register.html': '''{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
<div class="col-md-6">
<div class="card shadow">
<div class="card-header bg-primary text-white">
<h3 class="mb-0">Регистрация</h3>
</div>
<div class="card-body">
<form method="POST">
{{form.hidden_tag()}}
<div class="mb-3">
{{form.username.label(class="form-label")}}
{{form.username(class="form-control", placeholder="Введите имя")}}
{% if form.username.errors %}
<div class="text-danger small">{{form.username.errors[0]}}</div>
{% endif %}
</div>
<div class="mb-3">
{{form.email.label(class="form-label")}}
{{form.email(class="form-control", placeholder="example@mail.ru")}}
{% if form.email.errors %}
<div class="text-danger small">{{form.email.errors[0]}}</div>
{% endif %}
</div>
<div class="mb-3">
{{form.password.label(class="form-label")}}
{{form.password(class="form-control", placeholder="Минимум 6 символов")}}
</div>
<div class="mb-3">
{{form.confirm_password.label(class="form-label")}}
{{form.confirm_password(class="form-control", placeholder="Повторите пароль")}}
</div>
<div class="mb-3">
<label class="form-label">{{form.role.label.text}}</label>
<div>
{% for value, label in form.role.choices %}
<div class="form-check">
<input class="form-check-input" type="radio" name="role" value="{{value}}" id="role_{{value}}" {% if loop.first %}checked{% endif %}>
<label class="form-check-label" for="role_{{value}}">
<strong>{{label}}</strong> - {% if value == 'customer' %}заказываю работу{% else %}выполняю работу{% endif %}
</label>
</div>
{% endfor %}
</div>
</div>
{{form.submit(class="btn btn-primary w-100")}}
</form>
<hr>
<p class="text-center mb-0">Уже есть аккаунт? <a href="/login">Войти</a></p>
</div>
</div>
</div>
</div>
{% endblock %}''',

    'login.html': '''{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
<div class="col-md-5">
<div class="card shadow">
<div class="card-header bg-success text-white">
<h3 class="mb-0">Вход</h3>
</div>
<div class="card-body">
<form method="POST">
{{form.hidden_tag()}}
<div class="mb-3">
{{form.email.label(class="form-label")}}
{{form.email(class="form-control", placeholder="Ваш email")}}
</div>
<div class="mb-3">
{{form.password.label(class="form-label")}}
{{form.password(class="form-control", placeholder="Ваш пароль")}}
</div>
{{form.submit(class="btn btn-success w-100")}}
</form>
<hr>
<p class="text-center mb-0">Нет аккаунта? <a href="/register">Зарегистрироваться</a></p>
</div>
</div>
</div>
</div>
{% endblock %}''',

    'dashboard_customer.html': '''{% extends "base.html" %}
{% block content %}
<h2>Кабинет заказчика</h2>
<p class="text-muted">Добро пожаловать, {{current_user.username}}!</p>
<hr>
<a href="/create_order" class="btn btn-primary mb-3">Создать новый заказ</a>
<h4>Мои заказы</h4>
{% if orders %}
<div class="table-responsive">
<table class="table table-striped">
<thead class="table-dark">
<tr>
<th>ID</th>
<th>Название</th>
<th>Статус</th>
<th>Откликов</th>
<th>Дата</th>
<th>Действия</th>
</tr>
</thead>
<tbody>
{% for o in orders %}
<tr>
<td>{{o.id}}</td>
<td>{{o.title}}</td>
<td><span class="badge bg-info">{{o.status}}</span></td>
<td><span class="badge bg-secondary">{{o.responses|length}}</span></td>
<td>{{o.created_at.strftime('%d.%m.%Y')}}</td>
<td>
<a href="/order/{{o.id}}" class="btn btn-sm btn-primary">Подробнее</a>
</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
{% else %}
<div class="alert alert-info">
У вас пока нет заказов. Создайте первый заказ!
</div>
{% endif %}
{% endblock %}''',

    'dashboard_worker.html': '''{% extends "base.html" %}
{% block content %}
<h2>Кабинет работника</h2>
<p class="text-muted">Добро пожаловать, {{current_user.username}}!</p>
<hr>
<h4>Доступные заказы</h4>
{% if orders %}
<div class="row">
{% for o in orders %}
<div class="col-md-6 mb-3">
<div class="card">
<div class="card-body">
<h5 class="card-title">{{o.title}}</h5>
<p class="card-text">{{o.description[:100]}}...</p>
<small class="text-muted">Заказчик: {{o.client.username}}</small><br>
<small class="text-muted">Дата: {{o.created_at.strftime('%d.%m.%Y')}}</small>
</div>
<div class="card-footer">
<a href="/order/{{o.id}}" class="btn btn-sm btn-success">Откликнуться</a>
</div>
</div>
</div>
{% endfor %}
</div>
{% else %}
<div class="alert alert-warning">Сейчас нет доступных заказов</div>
{% endif %}
<hr>
<h4>Мои отклики</h4>
{% if responses %}
<ul class="list-group">
{% for r in responses %}
<li class="list-group-item">
<strong>{{r.order.title}}</strong><br>
<small>Статус: 
{% if r.status == 'waiting' %}<span class="badge bg-warning">Ожидание</span>
{% elif r.status == 'accepted' %}<span class="badge bg-success">Принят</span>
{% else %}<span class="badge bg-danger">Отклонён</span>
{% endif %}
</small>
</li>
{% endfor %}
</ul>
{% else %}
<p class="text-muted">Вы ещё не откликались на заказы</p>
{% endif %}
{% endblock %}''',

    'create_order.html': '''{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
<div class="col-md-8">
<div class="card shadow">
<div class="card-header bg-success text-white">
<h3 class="mb-0">Создать новый заказ</h3>
</div>
<div class="card-body">
<form method="POST" enctype="multipart/form-data">
{{form.hidden_tag()}}
<div class="mb-3">
{{form.title.label(class="form-label")}}
{{form.title(class="form-control", placeholder="Например: Разработка сайта")}}
</div>
<div class="mb-3">
{{form.description.label(class="form-label")}}
{{form.description(class="form-control", rows=6, placeholder="Опишите детали...")}}
</div>
<div class="mb-3">
{{form.file.label(class="form-label")}}
{{form.file(class="form-control")}}
<small class="text-muted">PDF, DOC, DOCX, TXT, ZIP</small>
</div>
<div class="d-flex gap-2">
{{form.submit(class="btn btn-success")}}
<a href="/dashboard" class="btn btn-secondary">Отмена</a>
</div>
</form>
</div>
</div>
</div>
</div>
{% endblock %}''',

    'orders.html': '''{% extends "base.html" %}
{% block content %}
<h2>Все доступные заказы</h2>
<p class="text-muted">Выберите интересующий проект</p>
<hr>
{% if orders %}
<div class="row">
{% for o in orders %}
<div class="col-md-6 mb-4">
<div class="card shadow-sm h-100">
<div class="card-body">
<h5 class="card-title">{{o.title}}</h5>
<p class="card-text">{{o.description[:150]}}{% if o.description|length > 150 %}...{% endif %}</p>
<div class="mb-2">
<small class="text-muted"><strong>Заказчик:</strong> {{o.client.username}}</small><br>
<small class="text-muted"><strong>Дата:</strong> {{o.created_at.strftime('%d.%m.%Y')}}</small>
</div>
<span class="badge bg-info">{{o.status}}</span>
</div>
<div class="card-footer bg-transparent">
<a href="/order/{{o.id}}" class="btn btn-sm btn-primary">Подробнее</a>
</div>
</div>
</div>
{% endfor %}
</div>
{% else %}
<div class="alert alert-warning">Заказов пока нет</div>
{% endif %}
{% endblock %}''',

    'order_detail_worker.html': '''{% extends "base.html" %}
{% block content %}
<div class="row">
<div class="col-md-8">
<div class="card">
<div class="card-header bg-primary text-white">
<h4 class="mb-0">{{order.title}}</h4>
</div>
<div class="card-body">
<p><strong>Описание:</strong></p>
<p>{{order.description}}</p>
<hr>
<p><small class="text-muted">Заказчик: {{order.client.username}}</small></p>
<p><small class="text-muted">Дата: {{order.created_at.strftime('%d.%m.%Y')}}</small></p>
{% if order.file_path %}
<p><small>Файл: {{order.file_path}}</small></p>
{% endif %}
</div>
</div>
</div>
<div class="col-md-4">
<div class="card">
<div class="card-header bg-success text-white">
<h5 class="mb-0">Откликнуться</h5>
</div>
<div class="card-body">
<form method="POST">
{{form.hidden_tag()}}
<div class="mb-3">
{{form.message.label(class="form-label")}}
{{form.message(class="form-control", rows=4, placeholder="Опишите как вы выполните заказ")}}
</div>
<div class="mb-3">
{{form.price.label(class="form-label")}}
{{form.price(class="form-control", placeholder="5000")}}
</div>
{{form.submit(class="btn btn-success w-100")}}
</form>
</div>
</div>
</div>
</div>
{% endblock %}''',

    'order_detail_customer.html': '''{% extends "base.html" %}
{% block content %}
<div class="card mb-4">
<div class="card-header bg-primary text-white">
<h4 class="mb-0">{{order.title}}</h4>
</div>
<div class="card-body">
<p><strong>Описание:</strong></p>
<p>{{order.description}}</p>
<p><strong>Статус:</strong> <span class="badge bg-info">{{order.status}}</span></p>
<p><small class="text-muted">Создан: {{order.created_at.strftime('%d.%m.%Y')}}</small></p>
</div>
</div>
<h4>Отклики ({{responses|length}})</h4>
{% if responses %}
<div class="row">
{% for r in responses %}
<div class="col-md-6 mb-3">
<div class="card {% if r.status == 'accepted' %}border-success{% endif %}">
<div class="card-body">
<h5 class="card-title">{{r.worker.username}}</h5>
<p class="card-text">{{r.message}}</p>
{% if r.price %}
<p><strong>Цена:</strong> {{r.price}} руб</p>
{% endif %}
<small class="text-muted">{{r.created_at.strftime('%d.%m.%Y')}}</small>
</div>
<div class="card-footer">
{% if r.status == 'waiting' %}
<a href="/accept_response/{{r.id}}" class="btn btn-sm btn-success">Принять</a>
{% elif r.status == 'accepted' %}
<span class="badge bg-success">Принят</span>
{% endif %}
</div>
</div>
</div>
{% endfor %}
</div>
{% else %}
<div class="alert alert-info">Пока нет откликов на этот заказ</div>
{% endif %}
{% endblock %}'''
}

# Создаём все файлы в UTF-8
for filename, content in templates.items():
    with open(f'templates/{filename}', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✅ {filename}')

print('\n🎉 Готово! Все файлы созданы в UTF-8!')
print('Теперь запусти: python app.py')