from datetime import datetime
import click
from flask.cli import with_appcontext
from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    IntegerField,
    ForeignKeyField,
)
from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()


class BaseModel(db_wrapper.Model):
    created = DateTimeField()
    modified = DateTimeField()

    def save(self, *args, **kwargs):
        self.modified = datetime.utcnow()
        super(BaseModel, self).save(*args, **kwargs)


class Work(BaseModel):
    title = CharField()


MODELS = [Work, ]


def create_tables():
    with db_wrapper.database:
        db_wrapper.database.create_tables(MODELS)


def drop_tables():
    with db_wrapper.database:
        db_wrapper.database.drop_tables(MODELS)


@click.command('init-db')
@with_appcontext
def init_db_command():
    # init tables
    create_tables()
    click.echo("Initialized the database.")


def init_app(app):
    app.cli.add_command(init_db_command)
