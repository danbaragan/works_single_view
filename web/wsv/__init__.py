import os
from pathlib import Path
from tempfile import TemporaryFile

from flask import Flask, Response, send_file
from flask_restful import Api

from . import db
from . import importer
from . import view


def create_app(test_config=None):
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
    api = Api(app)
    api.add_resource(view.WorksList, "/works")
    api.add_resource(view.WorksDetail, "/works/<string:iswc>")

    db.db_wrapper.init_app(app)
    db.db_wrapper.database.close()
    db.init_app(app)
    importer.init_app(app)

    @app.route('/hello')
    def hello():
        return "Hello world!"

    @app.route('/import')
    def import_csv():
        return "import"

    @app.route('/export')
    def export_csv():
        # this will be deleted at close / garbage collection
        file = TemporaryFile(mode="w+")
        importer.csv_data.export_csv(file)
        file.seek(0)
        # return send_file(file, mimetype="text/csv")
        return Response(
            file,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=works.csv"},
        )

    return app
