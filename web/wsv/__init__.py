import os
from pathlib import Path

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV')
    if env == 'development' or test_config:
        instance_path = Path(app.instance_path)
        instance_path.mkdir(parents=True, exist_ok=True)
        db_config = {
            'name': instance_path / os.getenv('DATABASE'),
            'engine': 'playhouse.pool.SqliteDatabase',
        }
    elif env == 'production':
        db_config = {
            'name': os.getenv('DATABASE'),
            'engine': 'playhouse.pool.PostgresqlDatabase',
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
        }

    app.config.from_mapping(
        DATABASE=db_config,
        SECRET_KEY=os.getenv('SECRET_KEY'),
    )

    if test_config:
        app.config.from_mapping(test_config)

    db.db_wrapper.init_app(app)
    db.db_wrapper.database.close()
    db.init_app(app)

    @app.route('/hello')
    def hello():
        return "Hello world!"

    return app
