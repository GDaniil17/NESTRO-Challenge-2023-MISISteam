import uuid
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
from flask_mail import Mail
from flask_mail import Message
import os


bp = Blueprint('cart', __name__)


@bp.route('/add_cart/<int:item_id>', methods=['POST'])
@login_required
def add_cart(item_id):
    db = get_db()
    print("get db!")
    # TODO
    db.execute(
        'INSERT INTO cart (user_id, item_id) '
        # f"VALUES ({g.user['id']}, {item_id})"
        ' SELECT ?, ?'
        ' WHERE NOT EXISTS (SELECT 1 FROM cart WHERE item_id = ?)',
        (g.user['id'], item_id, item_id)
    )
    db.commit()
    print("Item added!")
    # flash("Item successfully added to cart", 'success')
    return redirect(url_for('store.index'))


def read_file(path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(f"!!!!(((((()))))) {dir_path+'/'+path}")
    with open(dir_path+"/"+path, newline='', encoding='utf-8') as file:
        reader = csv.reader(file, quotechar='"')
        lines = [tuple(row) for row in reader]
    return (lines[0], lines[1:])


def table(path):
    headers, rows = read_file(path)  # 'youtubers_df.csv')
    return render_template('columns.html', headers=headers, rows=rows)


@bp.route('/preview/<int:item_id>', methods=['POST', 'GET'])
@login_required
def preview(item_id):
    db = get_db()
    print(f"get db!!!! {item_id}")
    file_name = db.execute(
        'SELECT file_name, id FROM item '
        f'WHERE id = {item_id}'
    ).fetchone()

    db.commit()
    print("Item selected!")
    path = f"static/files/{file_name['file_name']}"
    # flash("Item successfully added to cart", 'success')
    return table(path)


@bp.route('/checkout', methods=['GET'])
@login_required
def checkout():
    db = get_db()
    all = db.execute('Select * from cart').fetchall()
    print(all)
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
        print(item_dataset_author, i['dataset_author'], re.search(
            item_dataset_author, i['dataset_author']))
        if re.search(item_dataset_author, i['dataset_author'].lower()) is not None:
            new_items.append(i)

    return render_template('store/index.html', items=new_items)


@bp.route('/delete/<cart_item_id>', methods=['POST'])
@login_required
def delete_item(cart_item_id):
    print("HERE")
    db = get_db()
    print(cart_item_id)
    db.execute('DELETE FROM cart WHERE cart_id = ?', [cart_item_id])
    db.commit()
    return redirect(url_for('cart.checkout'))


def create_zip_archive(file_list, archive_name):
    print(archive_name)
    with zipfile.ZipFile(archive_name, 'w') as zip_file:
        for file_path in file_list:
            file_name = os.path.join(
                os.getcwd(),
                fr'marketplace\static\files\{file_path}'
            )
            print(f"filename!!!! {file_name}")
            # file_name = os.path.basename(file_path)
            zip_file.write(file_name, file_path)


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
    zip_name = 'dataset.zip'  # uuid.uuid4().hex+".zip"
    files = [item['original_file_name'] for item in cart_items]
    print(f"!!!!!!!!!!!!!!!!!! {files}")
    # create_zip_archive(files, zip_name)
    path = os.path.join(
        os.getcwd(),
        fr'marketplace\static\files\{zip_name}'
    )
    print("GOT")
    cache = tempfile.NamedTemporaryFile()
    print("!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!")
    print(path)
    path = path.replace("\\", "/")

    with open(path, 'rb') as fp:
        shutil.copyfileobj(fp, cache)
        cache.flush()
    cache.seek(0)
    print("?????????????")
    return send_file(cache, as_attachment=True, download_name=zip_name)


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
    print(dir_path+"/static/files/"+file_name['original_file_name'])
    return dir_path+"/static/files/"+file_name['original_file_name']


@bp.route('/download/<int:item_id>', methods=['POST'])
@login_required
def download_item(item_id):
    PATH = get_PATH_by_item_id(item_id)
    print("!!!!(((((()))))) ", PATH)
    if PATH:
        return send_file(PATH, as_attachment=True)
    else:
        flash('Файл не найден.')

    # return redirect(url_for('cart.checkout'))


@bp.route('/mail/<int:item_id>', methods=['POST'])
@login_required
def mail_item(item_id):
    import os
    print("HERE")
    PATH = get_PATH_by_item_id(item_id)
    db = get_db()
    file_name = db.execute(
        'SELECT id, item_description, item_name FROM item '
        f'WHERE id = {item_id}'
    ).fetchone()

    print("!!!!(****** ", PATH, os.path.isfile(PATH))
    email_address = ''
    subject = 'Датасет - '+str(file_name['item_name'])
    body = 'Описание датасета - ' + str(file_name['item_description'])
    attachment_path = PATH
    mailto_link = f"mailto:{email_address}?subject={subject}&body={body}&attachments={attachment_path}"

    return redirect(mailto_link)
