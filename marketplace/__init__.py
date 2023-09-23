import os

from flask import Flask, flash, request, redirect, url_for
from . import db
from . import auth
from . import store
from . import cart
from flask import send_from_directory
from flask import render_template
from werkzeug.utils import secure_filename
import csv

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'marketplace.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello :)
    @app.route('/hello')
    def hello():
        return "Hello World!! 🤡"

    def read_file(path):
        with open(path, newline='') as file:
            reader = csv.reader(file, quotechar='"')
            lines = [tuple(row) for row in reader]
        return (lines[0], lines[1:])

    # headers = ("Rank", "Username", "Categories", "Subscribers", "Country", "Visits", "Likes", "Comments" и "Links")
    # rows = (('Боба Биба Бобович', '18', 'Male'),
    #         ('Боба Биба Бобович', '20', 'Male')
    #         )

    @app.route('/table/<path>')
    def table(path):
        headers, rows = read_file(path)  # 'youtubers_df.csv')
        return render_template('columns.html', headers=headers, rows=rows)

    @app.route('/item')
    def item_path():
        rows = [
            {'item_id': "1", 'dataset_name': "Датасет 1", 'image_link': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
                'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '10000009'},
            {'item_id': "2", 'dataset_name': "Датасет 2", 'image_link': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
                'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '10000009'},
            {'item_id': "3", 'dataset_name': "Датасет 3", 'image_link': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
                'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '10000009'},
            {'item_id': 4, 'dataset_name': "Датасет 4", 'image_link': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
                'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '10000009'},
            {'item_id': 5, 'dataset_name': "Датасет 5", 'image_link': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
                'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '10000009'},
            {'item_id': 6, 'dataset_name': "Датасет 6", 'image_link': 'https://avatars.mds.yandex.net/i?id=39cddff1f46a9e611501ea7b6c804ab4_l-5222489-images-thumbs&n=13', 'dataset_category': 'porn',
                'dataset_description': 'really', 'dataset_author': 'your m', 'dataset_number_views': '10000009'}
        ]
        return render_template('item.html', rows=rows)

    @app.route('/columns')
    def get_columns():
        return render_template('columns.html')

    @app.route('/loader')
    def loader():
        return render_template('loader.html')

    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
    app.config['UPLOAD_PATH'] = 'uploads'
    app.config['UPLOAD_FOLDER'] = ''

    @app.errorhandler(413)
    def too_large(e):
        return "File is too large", 413

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/upload_file', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('upload_file', name=filename))
        return render_template('loader.html')

    # initialize app and blueprints
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(store.bp)
    app.register_blueprint(cart.bp)
    app.add_url_rule('/', endpoint='index')

    return app
