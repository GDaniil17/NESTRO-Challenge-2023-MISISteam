import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_all_items():
    db = get_db()
    query = 'SELECT * FROM cart'
    items = db.execute(query).fetchall()
    item_list = []
    for item in items:
        item_dict = {
            'item_name': item['item_name'],
            'name': item['name'],
            'description': item['description'],
            'image': item['image'],
            'price': item['price']
        }
        item_list.append(item_dict)
    return item_list


def get_item_by_id(item_id):
    db = get_db()
    query = 'SELECT * FROM cart WHERE item_id = ?'
    item = db.execute(query, (item_id,)).fetchone()
    if item:
        return item
    return None
