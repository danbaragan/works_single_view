import os
from pathlib import Path

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__)
    instance_path = Path(app.instance_path)
    app.config.from_mapping(
        DATABASE={
            'name': instance_path / os.getenv('DATABASE_URL'),
            'engine': 'playhouse.pool.SqliteDatabase',
        },
        SECRET_KEY=os.getenv('SECRET_KEY'),
    )

    if test_config:
        app.config.from_mapping(test_config)

    instance_path.mkdir(parents=True, exist_ok=True)

    db.db_wrapper.init_app(app)
    db.db_wrapper.database.close()
    db.init_app(app)

    @app.route('/hello')
    def hello():
        return "Hello world!"

    return app
