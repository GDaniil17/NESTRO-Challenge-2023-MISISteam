import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from marketplace.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    import re
    error = []
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        isAdmin = request.form.get('isAdmin')
        db = get_db()

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
            error.append('Пользователь {} уже зарегистрирован'.format(username))

        admin = 1 if isAdmin else 0
        if not error:
            db.execute(
                'INSERT INTO user (name, username, password, admin) VALUES (?, ?, ?, ?)',
                (name, username, generate_password_hash(password), admin)
            )
            db.commit()
            return redirect(url_for('auth.login', error=error))
    return render_template('auth/register.html', error = error)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = []
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error.append('Пользователь не найден')
        elif not check_password_hash(user['password'], password):
            error.append('Неправильный пароль')

        if not error:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
    elif request.method == "GET":
        session.clear()
    return render_template('auth/login.html', error=error)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def admin_only(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user['admin']:
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view
