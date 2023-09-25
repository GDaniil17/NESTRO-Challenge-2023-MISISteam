from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import os
import uuid
from werkzeug.utils import secure_filename
import pandas as pd

from marketplace.auth import login_required, admin_only
from marketplace.db import get_db
from flask import render_template, flash, redirect, url_for
from .db import get_item_by_id

# Создаем Blueprint с именем 'store'
bp = Blueprint('store', __name__)
# Получаем путь к текущей директории
dir_path = os.path.dirname(os.path.realpath(__file__))
# Устанавливаем путь к папке с изображениями
IMG_FOLDER = dir_path + '/static/img'
# Устанавливаем путь к папке с файлами
FILE_FOLDER = dir_path + '/static/files'


@bp.route('/')
def index():
    # Если пользователь не авторизован, перенаправляем на страницу входа
    if not g.user:
        return redirect(url_for('auth.login'))
    # Получаем доступ к базе данных
    db = get_db()

    # Создаем таблицу item, если она не существует
    db.execute('CREATE TABLE IF NOT EXISTS item (id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'item_name TEXT NOT NULL,'
               'item_description TEXT,'
               'item_image BLOB,'
               'dataset_author TEXT NOT NULL,'
               'file_name TEXT NOT NULL,'
               'secured_name TEXT NOT NULL,'
               'original_file_name TEXT NOT NULL)')

    # Создаем таблицу cart, если она не существует
    db.execute('CREATE TABLE IF NOT EXISTS cart (cart_id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'user_id INTEGER NOT NULL,'
               'item_id INTEGER NOT NULL,'
               'FOREIGN KEY (user_id) REFERENCES user (id),'
               'FOREIGN KEY (item_id) REFERENCES item (id))')

    # Получаем все товары из базы данных
    items = db.execute(
        'SELECT *'
        ' FROM item i'
    ).fetchall()

    # Отображаем главную страницу магазина с товарами
    return render_template('store/index.html', items=items)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
# @admin_only
def create():
    # Если метод запроса - POST, значит форма была отправлена
    if request.method == 'POST':
        # Получаем данные из формы
        data = request.values.to_dict()
        item_name = data["item_name"]
        item_description = data["item_description"]
        item_image = request.files["item_image"]
        item_file = request.files["item_file"]
        errors = []
        dataset_author = data["dataset_author"]

        # Проверяем, был ли выбран файл с данными
        if len(item_file.filename) != 0:
            secure_filename(item_file.filename)
            secured_name = uuid.uuid4().hex
            file_name = secured_name + '.'+(item_file.filename.split('.')[-1])
            original_file_name = file_name

            # Сохраняем файл с данными в указанную папку
            item_file.save(os.path.join(FILE_FOLDER, file_name))
            # Если файл имеет расширение .xlsx, конвертируем его в .csv
            if (item_file.filename.split('.')[-1]) == "xlsx":
                data = pd.read_excel(os.path.join(FILE_FOLDER, file_name))
                PATH = os.path.join(FILE_FOLDER, secured_name)
                data.to_csv(PATH+'.csv', index=False)
                file_name = secured_name + '.csv'

        else:
            error = 'Нужно выбрать файл с данными'
            errors.append(error)
            flash(error)

        # Проверяем, было ли указано описание товара
        if not item_description:
            error = 'Описание обязательно'
            errors.append(error)
            flash(error)
        # Проверяем, было ли выбрано изображение товара
        if not item_image:
            error = 'Изображение обязательно'
            errors.append(error)
            flash(error)
        # Проверяем, был ли выбран файл с данными
        if not item_file:
            error = 'Набор данных обязателен'
            errors.append(error)
            flash(error)

        # Если было выбрано изображение товара, сохраняем его в указанную папку
        if item_image:
            secure_filename(item_image.filename)
            item_image.save(os.path.join(IMG_FOLDER, item_image.filename))

        # Проверяем, было ли указано название товара
        if not item_name:
            error = 'Заголовок обязателен'
            errors.append(error)
            flash(error)
        else:
            try:
                # Получаем доступ к базе данных
                db = get_db()
                # Выполняем SQL-запрос для добавления нового товара в таблицу item
                db.execute(
                    'INSERT INTO item (item_name, item_description, item_image, dataset_author, secured_name, file_name, original_file_name)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (item_name, item_description, item_image.filename,
                     dataset_author, secured_name, file_name, original_file_name)
                )
                # Применяем изменения в базе данных
                db.commit()

                flash(item_name + ' was added to the store', 'success')
            except:
                return render_template('store/create.html', errors=errors)

    # Отображаем страницу с формой для создания товара
    return render_template('store/create.html')


@bp.route('/delete_cart_item/<int:item_id>', methods=['POST'])
@login_required
@admin_only
def delete(item_id):
    # Получаем доступ к базе данных
    db = get_db()
    # Выполняем SQL-запрос для удаления элемента из таблицы item по заданному id
    db.execute('DELETE FROM item WHERE id = ?', [item_id])
    # Применяем изменения в базе данных
    db.commit()
    # Перенаправляем пользователя на главную страницу магазина
    return redirect(url_for('store.index'))


@bp.route('/store/item/<int:item_id>')
def view_item(item_id):
    # Получаем информацию о товаре по заданному id
    item = get_item_by_id(item_id)
    # Если товар найден, отображаем страницу с информацией о товаре
    if item:
        return render_template('store/item.html', item=item)
    # Если товар не найден, выводим сообщение об ошибке
    flash('Item not found')
    # Перенаправляем пользователя на главную страницу магазина
    return redirect(url_for('store.index'))
