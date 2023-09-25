# Импортируем необходимые модули и функции
import uuid  # Модуль для работы с уникальными идентификаторами
import zipfile  # Модуль для работы с ZIP-архивами
import shutil  # Модуль для работы с файлами и директориями
import tempfile  # Модуль для работы с временными файлами и директориями
from flask import (  # Модуль Flask для работы с веб-приложением
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, redirect, Flask
)
import csv  # Модуль для работы с CSV-файлами

from marketplace.db import get_db  # Модуль для работы с базой данных
# Декоратор функции для проверки наличия аутентификации
from marketplace.auth import login_required
# Модуль Flask-Mail для отправки электронной почты
from flask_mail import Mail, Message
import os  # Модуль для работы с операционной системой

# Создаем экземпляр Blueprint с именем 'cart'
bp = Blueprint('cart', __name__)

# Функция для добавления товара в корзину


@bp.route('/add_cart/<int:item_id>', methods=['POST'])
@login_required  # Декоратор для проверки наличия аутентификации
def add_cart(item_id):
    db = get_db()
    # TODO
    db.execute(
        'INSERT INTO cart (user_id, item_id) '
        # f"VALUES ({g.user['id']}, {item_id})"
        ' SELECT ?, ?'
        ' WHERE NOT EXISTS (SELECT 1 FROM cart WHERE item_id = ?)',
        (g.user['id'], item_id, item_id)
    )
    db.commit()
    return redirect(url_for('store.index'))

# Функция для чтения CSV-файла


def read_file(path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path+"/"+path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file, quotechar='"')
        lines = [tuple(row) for row in reader]
    return (lines[0], lines[1:])

# Функция для отображения таблицы из CSV-файла


def table(path):
    headers, rows = read_file(path)  # Читаем данные из CSV-файла
    # Отображаем таблицу в HTML-шаблоне
    return render_template('columns.html', headers=headers, rows=rows)

# Функция для предварительного просмотра товара


@bp.route('/preview/<int:item_id>', methods=['POST', 'GET'])
@login_required  # Декоратор для проверки наличия аутентификации
def preview(item_id):
    db = get_db()
    file_name = db.execute(
        'SELECT file_name, id FROM item '
        f'WHERE id = {item_id}'
    ).fetchone()

    db.commit()
    path = f"static/files/{file_name['file_name']}"
    return table(path)

# Функция для оформления заказа


@bp.route('/checkout', methods=['GET'])
@login_required  # Декоратор для проверки наличия аутентификации
def checkout():
    db = get_db()
    all = db.execute('Select * from cart').fetchall()
    cart_items = db.execute(
        'SELECT cart_id, i.item_name, i.dataset_author, i.item_description, i.item_image FROM cart c'
        ' INNER JOIN item i ON c.item_id = i.id'
        ' WHERE c.user_id = ?',
        [g.user['id']]
    ).fetchall()
    return render_template('cart/checkout.html', cart_items=cart_items)


# Функция для фильтрации товаров по автору набора данных
@bp.route('/tag/<item_dataset_author>', methods=['GET'])
@login_required  # Декоратор для проверки наличия аутентификации
def tag(item_dataset_author):
    import re
    item_dataset_author = item_dataset_author.strip().lower()
    item_dataset_author = item_dataset_author.replace(" ", "*")
    db = get_db()

    items = db.execute(
        'SELECT *'
        ' FROM item i'
    ).fetchall()

    new_items = []
    for i in items:
        if re.search(item_dataset_author, i['dataset_author'].lower()) is not None:
            new_items.append(i)

    return render_template('store/index.html', items=new_items)

# Функция для удаления товара из корзины


@bp.route('/delete/<cart_item_id>', methods=['POST'])
@login_required  # Декоратор для проверки наличия аутентификации
def delete_item(cart_item_id):
    db = get_db()
    db.execute('DELETE FROM cart WHERE cart_id = ?', [cart_item_id])
    db.commit()
    return redirect(url_for('cart.checkout'))

# Функция для создания ZIP-архива


def create_zip_archive(file_list, archive_name):
    with zipfile.ZipFile(archive_name, 'w') as zip_file:
        for file_path in file_list:
            file_name = os.path.join(
                os.getcwd(),
                fr'marketplace\static\files\{file_path}'
            )
            zip_file.write(file_name, file_path)

# Функция для скачивания ZIP-архива с товарами из корзины


@bp.route('/download_zip', methods=['POST'])
@login_required  # Декоратор для проверки наличия аутентификации
def download_zip():
    db = get_db()
    cart_items = db.execute(
        'SELECT cart_id, i.item_name, i.dataset_author, i.item_description, i.original_file_name FROM cart c'
        ' INNER JOIN item i ON c.item_id = i.id'
        ' WHERE c.user_id = ?',
        [g.user['id']]
    ).fetchall()
    db.commit()
    zip_name = 'dataset.zip'  # uuid.uuid4().hex+".zip"
    files = [item['original_file_name'] for item in cart_items]
    # create_zip_archive(files, zip_name)
    path = os.path.join(
        os.getcwd(),
        fr'marketplace\static\files\{zip_name}'
    )
    cache = tempfile.NamedTemporaryFile()
    path = path.replace("\\", "/")

    with open(path, 'rb') as fp:
        shutil.copyfileobj(fp, cache)
        cache.flush()
    cache.seek(0)
    return send_file(cache, as_attachment=True, download_name=zip_name)

# Функция для получения пути к файлу товара по его идентификатору


def get_PATH_by_item_id(item_id):
    db = get_db()
    file_name = db.execute(
        'SELECT original_file_name, id FROM item '
        f'WHERE id = {item_id}'
    ).fetchone()
    # lsx csv
    db.commit()
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path+"/static/files/"+file_name['original_file_name']

# Функция для скачивания товара


@bp.route('/download/<int:item_id>', methods=['POST'])
@login_required  # Декоратор для проверки наличия аутентификации
def download_item(item_id):
    PATH = get_PATH_by_item_id(item_id)
    if PATH:
        return send_file(PATH, as_attachment=True)
    else:
        flash('Файл не найден.')


# Функция для отправки товара по электронной почте
@bp.route('/mail/<int:item_id>', methods=['POST'])
@login_required  # Декоратор для проверки наличия аутентификации
def mail_item(item_id):
    PATH = get_PATH_by_item_id(item_id)
    db = get_db()
    file_name = db.execute(
        'SELECT id, item_description, item_name FROM item '
        f'WHERE id = {item_id}'
    ).fetchone()
    email_address = ''
    subject = 'Датасет - '+str(file_name['item_name'])
    body = 'Описание датасета - ' + str(file_name['item_description'])
    attachment_path = PATH
    mailto_link = f"mailto:{email_address}?subject={subject}&body={body}&attachments={attachment_path}"

    return redirect(mailto_link)
