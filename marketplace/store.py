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
    items = db.execute(
        'SELECT *'
        ' FROM item i'
    ).fetchall()
    return render_template('store/index.html', items=items)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
@admin_only
def create():
    if request.method == 'POST':
        item_name = request.form["name"]
        item_description = request.form["description"]
        item_image = request.files["image"]
        price = request.form["price"]

        if item_image:
            secure_filename(item_image.filename)
            item_image.save(os.path.join(UPLOAD_FOLDER, item_image.filename))

        if not item_name:
            error = 'Title is required.'
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO item (item_name, item_description, item_image, price)'
                ' VALUES (?, ?, ?, ?)',
                (item_name, item_description, item_image.filename, price)
            )
            db.commit()
            flash(item_name + ' was added to the store', 'success')

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
