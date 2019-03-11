import os
from pathlib import Path

from flask import Flask
from flask_restful import Api


def create_app(test_config=None):
    from . import db
    from . import importer
    from . import view

    app = Flask(__name__)

    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)
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

    app.register_blueprint(view.app_blueprint)

    api = Api(app, '/api/v1')
    api.add_resource(view.WorksList, "/works")
    api.add_resource(view.WorksDetail, "/works/<string:iswc>")

    db.db_wrapper.init_app(app)
    db.db_wrapper.database.close()
    db.init_app(app)
    importer.init_app(app)

    return app
