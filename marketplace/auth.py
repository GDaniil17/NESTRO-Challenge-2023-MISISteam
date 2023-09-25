# Импортируем необходимые модули и функции
import functools  # Модуль для работы с функциями высшего порядка
from flask import (  # Модуль Flask для работы с веб-приложением
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
# Модуль для работы с хэшированием паролей
from werkzeug.security import check_password_hash, generate_password_hash
from marketplace.db import get_db  # Модуль для работы с базой данных

# Создаем экземпляр Blueprint с именем 'auth' и префиксом URL '/auth'
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Функция для обработки запросов на регистрацию пользователей


@bp.route('/register', methods=['GET', 'POST'])
def register():
    import re
    error = []  # Список для хранения ошибок
    if request.method == 'POST':  # Если метод запроса - POST
        # Получаем данные из формы
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        isAdmin = request.form.get('isAdmin')
        db = get_db()  # Получаем объект базы данных

        # Проверяем наличие и корректность введенных данных
        if not username:
            error.append('Логин обязателен')
        elif re.fullmatch("([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", username) is None:
            error.append("Некорректный почтовый адрес")
        elif not password:
            error.append('Пароль обязателен')
        elif len(password) < 8:
            error.append('Пароль слишком короткий. \nМинимум 8 символов')
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error.append(
                'Пользователь {} уже зарегистрирован'.format(username))

        admin = 1 if isAdmin else 0  # Преобразуем isAdmin в числовое значение
        if not error:  # Если ошибок нет
            # Выполняем вставку данных в базу данных
            db.execute(
                'INSERT INTO user (name, username, password, admin) VALUES (?, ?, ?, ?)',
                (name, username, generate_password_hash(password), admin)
            )
            db.commit()  # Фиксируем изменения в базе данных
            # Перенаправляем на страницу входа
            return redirect(url_for('auth.login', error=error))
    # Отображаем страницу с формой регистрации
    return render_template('auth/register.html', error=error)

# Функция для обработки запросов на вход в систему


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = []  # Список для хранения ошибок
    if request.method == 'POST':  # Если метод запроса - POST
        # Получаем данные из формы
        username = request.form['username']
        password = request.form['password']
        db = get_db()  # Получаем объект базы данных
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()  # Ищем пользователя в базе данных по логину

        if user is None:
            error.append('Пользователь не найден')
        elif not check_password_hash(user['password'], password):
            error.append('Неправильный пароль')

        if not error:  # Если ошибок нет
            session.clear()  # Очищаем сессию
            # Сохраняем идентификатор пользователя в сессии
            session['user_id'] = user['id']
            # Перенаправляем на главную страницу
            return redirect(url_for('index'))
    elif request.method == "GET":  # Если метод запроса - GET
        session.clear()  # Очищаем сессию
    # Отображаем страницу с формой входа
    return render_template('auth/login.html', error=error)


@bp.before_app_request
def load_logged_in_user():
    # Получаем идентификатор пользователя из сессии
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None  # Если идентификатор пользователя отсутствует, устанавливаем g.user в None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()  # Ищем пользователя в базе данных по идентификатору

# Функция для выполнения выхода из системы


@bp.route('/logout')
def logout():
    session.clear()  # Очищаем сессию
    return redirect(url_for('index'))  # Перенаправляем на главную страницу

# Декоратор функции для проверки наличия аутентификации


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:  # Если пользователь не авторизован
            # Перенаправляем на страницу входа
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# Декоратор функции для проверки административных прав


def admin_only(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user['admin']:  # Если у пользователя нет административных прав
            # Перенаправляем на главную страницу
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view
