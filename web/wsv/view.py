import io

from flask import Blueprint
from flask import Response, request, render_template, flash, url_for, redirect
from flask_restful import Resource
from werkzeug.exceptions import BadRequestKeyError
from tempfile import TemporaryFile

from .db import *
from .serializer import *
from . import importer

app_blueprint = Blueprint('app', __name__)


@app_blueprint.route('/hello/')
@app_blueprint.route('/hello/<name>')
def hello(name='world'):
    return render_template('hello.html', name=name)


@app_blueprint.route('/import', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        try:
            f = request.files['csv_file']
            stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        except (BadRequestKeyError, UnicodeDecodeError):
            return "no/bad file", 400

        importer.csv_data.import_csv(stream)
        flash(f'{f.filename} imported')
        redirect(url_for('import_csv'))
    return render_template('import.html')


@app_blueprint.route('/export')
def export_csv():
    # this will be deleted at close / garbage collection
    file = TemporaryFile(mode="w+")
    importer.csv_data.export_csv(file)
    file.seek(0)
    return Response(
        file,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=works.csv"},
    )


class WorksList(Resource):
    def get(self):
        works_q = Work.select()
        works = works_schema.dump(works_q).data
        return {
            'works': works
        }


class WorksDetail(Resource):
    def get(self, iswc):
        try:
            w = Work.get(Work.iswc == iswc)
        except Work.DoesNotExist:
            return {}, 404
        work = work_schema.dump(w).data
        return {
            'work': work
        }
