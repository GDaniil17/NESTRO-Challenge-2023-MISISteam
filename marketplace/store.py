from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import os
from werkzeug.utils import secure_filename

from marketplace.auth import login_required, admin_only
from marketplace.db import get_db
from flask import render_template, flash, redirect, url_for
from .db import get_all_items, get_item_by_id


bp = Blueprint('store', __name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = dir_path + '/static/img'


@bp.route('/')
def index():
    if not g.user:
        return redirect(url_for('auth.login'))
    db = get_db()
    # db.execute("DROP TABLE cart")
    # db.execute("DROP TABLE item")

    # db.execute('CREATE TABLE item (id INTEGER PRIMARY KEY AUTOINCREMENT,'
    #            'item_name TEXT NOT NULL,'
    #            'item_description TEXT,'
    #            'item_image BLOB,'
    #            'dataset_author TEXT NOT NULL)')

    # db.execute('CREATE TABLE cart (cart_id INTEGER PRIMARY KEY AUTOINCREMENT,'
    #            'user_id INTEGER NOT NULL,'
    #            'item_id INTEGER NOT NULL,'
    #            'FOREIGN KEY (user_id) REFERENCES user (id),'
    #            'FOREIGN KEY (item_id) REFERENCES item (id))')

    items = db.execute(
        'SELECT *'
        ' FROM item i'
    ).fetchall()
    print(items)
    # items = [
    #     {'id': 0, 'dataset_name': "Датасет 1", 'item_image': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
    #      'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '10009'},
    #     {'id': 1, 'dataset_name': "Датасет 2", 'item_image': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
    #      'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '1009'},
    #     {'id': 2, 'dataset_name': "Датасет 3", 'item_image': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
    #      'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '109'},
    #     {'id': 3, 'dataset_name': "Датасет 4", 'item_image': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
    #      'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '19'},
    #     {'id': 4, 'dataset_name': "Датасет 5", 'item_image': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
    #      'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '9'},
    #     {'id': 5, 'dataset_name': "Датасет 6", 'item_image': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
    #      'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '91'}
    # ]
    return render_template('store/index.html', items=items)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
# @admin_only
def create():
    print(f"!!!!!!!!!!!!! {request.method}")
    if request.method == 'POST':
        print(f"!!!!!!!!!!!!! {request.values}")
        data = request.values.to_dict()
        item_name = data["item_name"]
        print("!!!!!!!!!!!!! 2")
        item_description = data["item_description"]
        print("!!!!!!!!!!!!! 3")
        item_image = request.files["item_image"]
        print("!!!!!!!!!!!!! 4")
        dataset_author = data["dataset_author"]

        print("!!!!!!!!!!!!! 1")
        if item_image:
            secure_filename(item_image.filename)
            item_image.save(os.path.join(UPLOAD_FOLDER, item_image.filename))

        print("!!!!!!!!!!!!! 2")
        if not item_name:
            error = 'Title is required.'
            flash(error)
        else:
            db = get_db()
            print("Get to DB")
            print((item_name, item_description, item_image.filename, dataset_author))
            db.execute(
                'INSERT INTO item (item_name, item_description, item_image, dataset_author)'
                ' VALUES (?, ?, ?, ?)',
                (item_name, item_description, item_image.filename, dataset_author)
            )
            db.commit()
            print(item_name + ' was added to the store', 'success')
            flash(item_name + ' was added to the store', 'success')
        print("!!!!!!!!!!!!! 3")

    return render_template('store/create.html')


@bp.route('/delete_cart_item/<int:item_id>', methods=['POST'])
@login_required
@admin_only
def delete(item_id):
    db = get_db()
    db.execute('DELETE FROM item WHERE id = ?', [item_id])
    db.commit()
    return redirect(url_for('store.index'))


# @bp.route('/store')
# def index():
#     items = get_all_items()
#     return render_template('store/index.html', items=items)


# @bp.route('/store/item/<int:item_id>')
# def view_item(item_id):
#     db = get_db()
#     item = db.get_item_by_id(item_id)
#     if item:
#         return render_template('store/item.html', item=item)
#     flash('Item not found')
#     return redirect(url_for('store.index'))


@bp.route('/store/item/<int:item_id>')
def view_item(item_id):
    item = get_item_by_id(item_id)
    if item:
        return render_template('store/item.html', item=item)
    flash('Item not found')
    return redirect(url_for('store.index'))
