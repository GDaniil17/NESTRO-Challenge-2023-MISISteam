import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# Получение соединения с базой данных


def get_db():
    if 'db' not in g:
        # Если соединение с базой данных еще не установлено, устанавливаем его
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# Закрытие соединения с базой данных


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# Инициализация базы данных


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        # Чтение SQL-скрипта из файла и выполнение его на базе данных
        db.executescript(f.read().decode('utf8'))

# Команда CLI для инициализации базы данных


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# Инициализация приложения Flask


def init_app(app):
    # Регистрация функции закрытия базы данных при завершении работы приложения
    app.teardown_appcontext(close_db)
    # Регистрация команды CLI для инициализации базы данных
    app.cli.add_command(init_db_command)

# Получение всех элементов


def get_all_items():
    db = get_db()
    query = 'SELECT * FROM cart'
    items = db.execute(query).fetchall()
    item_list = []
    for item in items:
        # Преобразование каждого элемента в словарь
        item_dict = {
            'item_name': item['item_name'],
            'name': item['name'],
            'description': item['description'],
            'image': item['image'],
            'price': item['price']
        }
        item_list.append(item_dict)
    return item_list

# Получение элемента по идентификатору


def get_item_by_id(item_id):
    db = get_db()
    query = 'SELECT * FROM cart WHERE item_id = ?'
    item = db.execute(query, (item_id,)).fetchone()
    if item:
        return item
    return None
