import re
import zipfile
import shutil
import tempfile
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, redirect, Flask
)
import csv

from marketplace.db import get_db
from marketplace.auth import login_required
from flask import Blueprint, g, flash, redirect, url_for
import os


bp = Blueprint('cart', __name__)

@bp.route('/add_cart/<int:item_id>', methods=['POST'])
@login_required
def add_cart(item_id):
    db = get_db()
    db.execute(
        'INSERT INTO cart (user_id, item_id) '
        ' SELECT ?, ?'
        ' WHERE NOT EXISTS (SELECT 1 FROM cart WHERE item_id = ?)',
        (g.user['id'], item_id, item_id)
    )
    db.commit()
    return redirect(url_for('store.index'))


def read_file(path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path+"/"+path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file, quotechar='"')
        lines = [tuple(row) for row in reader]
    return (lines[0], lines[1:])


def table(path):
    headers, rows = read_file(path)
    return render_template('columns.html', headers=headers, rows=rows)


@bp.route('/preview/<int:item_id>', methods=['POST', 'GET'])
@login_required
def preview(item_id):
    db = get_db()
    file_name = db.execute(
        'SELECT file_name, id FROM item '
        f'WHERE id = {item_id}'
    ).fetchone()

    db.commit()
    path = f"static/files/{file_name['file_name']}"
    return table(path)


@bp.route('/checkout', methods=['GET'])
@login_required
def checkout():
    db = get_db()
    cart_items = db.execute(
        'SELECT cart_id, i.item_name, i.dataset_author, i.item_description, i.item_image FROM cart c'
        ' INNER JOIN item i ON c.item_id = i.id'
        ' WHERE c.user_id = ?',
        [g.user['id']]
    ).fetchall()
    return render_template('cart/checkout.html', cart_items=cart_items)


@bp.route('/tag/<item_dataset_author>', methods=['GET'])
@login_required
def tag(item_dataset_author):
    title = f"{item_dataset_author.strip()}"
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

    return render_template('store/index.html', items=new_items, title=title)


@bp.route('/delete/<cart_item_id>', methods=['POST'])
@login_required
def delete_item(cart_item_id):
    db = get_db()
    db.execute('DELETE FROM cart WHERE cart_id = ?', [cart_item_id])
    db.commit()
    return redirect(url_for('cart.checkout'))


def create_zip_archive(file_list, archive_name):
    with zipfile.ZipFile(archive_name, 'w') as zip_file:
        for file_path in file_list:
            full_path = os.path.join(os.getcwd(), 'marketplace', 'static', 'files', file_path)
            zip_file.write(full_path, file_path)


@bp.route('/download_zip', methods=['POST'])
@login_required
def download_zip():
    db = get_db()
    cart_items = db.execute(
        'SELECT cart_id, i.item_name, i.dataset_author, i.item_description, i.original_file_name FROM cart c'
        ' INNER JOIN item i ON c.item_id = i.id'
        ' WHERE c.user_id = ?',
        [g.user['id']]
    ).fetchall()
    db.commit()
    zip_name = 'ziped_data.zip'# uuid.uuid4().hex+".zip"
    files = [item['original_file_name'] for item in cart_items]
    create_zip_archive(files, zip_name)
    path = os.path.join(
        os.getcwd(),
        fr'marketplace/static/files/{zip_name}'
    )
    cache = tempfile.NamedTemporaryFile()
    with open(path, 'rb') as fp:
        shutil.copyfileobj(fp, cache)
        cache.flush()
    cache.seek(0)
    return send_file(cache, as_attachment=True, download_name=zip_name)



def get_PATH_by_item_id(item_id):
    db = get_db()
    file_name = db.execute(
        'SELECT original_file_name, id FROM item '
        f'WHERE id = {item_id}'
    ).fetchone()
    db.commit()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path+"/static/files/"+file_name['original_file_name']


@bp.route('/download/<int:item_id>', methods=['POST'])
@login_required
def download_item(item_id):
    PATH = get_PATH_by_item_id(item_id)
    if PATH:
        return send_file(PATH, as_attachment=True)
    else:
        flash('Файл не найден.')


@bp.route('/mail/<int:item_id>', methods=['POST'])
@login_required
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
