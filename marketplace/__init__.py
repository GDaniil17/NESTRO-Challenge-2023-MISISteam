import os

from flask import Flask
from . import db
from . import auth
from . import store
from . import cart
from flask import send_from_directory
from flask import render_template
import csv


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
        return render_template('table.html', headers=headers, rows=rows)

    # initialize app and blueprints
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(store.bp)
    app.register_blueprint(cart.bp)
    app.add_url_rule('/', endpoint='index')

    return app
