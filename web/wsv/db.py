from datetime import datetime
from fuzzywuzzy import fuzz
import click

from flask.cli import with_appcontext
from peewee import *
from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()


class BaseModel(db_wrapper.Model):
    created = DateTimeField()
    modified = DateTimeField()

    def save(self, *args, **kwargs):
        self.modified = datetime.utcnow()
        super(BaseModel, self).save(*args, **kwargs)

    def better_field(self, name, value):
        # TODO restrict this only to char fields
        fld = getattr(self, name)
        if value == fld:
            return False
        # TODO This is some simplified way to determine if some name is better than the one we have stored
        # TODO improve the fuzzy match for typos (match against a dictionary? what language?

        # fuzzy match for unicode, allow 2 chars to differ
        if len(value) == len(fld):
            current_fld_unicode = False
            try:
                value.encode('ascii')
                # value does not have improved unicode chars
                return False
            except UnicodeEncodeError:
                # value is unicode rich
                pass

            try:
                fld.encode('ascii')
                # value does not have improved unicode chars
            except UnicodeEncodeError:
                current_fld_unicode = True
            r = fuzz.ratio(value, fld)
            if current_fld_unicode:
                # both unicode, one letter diff - maybe the new import is better assuming it is newer
                if r >= 90:
                    return True
                # our version is not unicode, allow up to 3 letter diff
                elif r >= 70:
                    return True

            return False

        # better if:
        # We have more info in the new value
        # We don't trim out information from the current value (we add words)
        if len(value) > len(fld):
            current_set = set(fld.split())
            new_set = set(value.split())
            if current_set < new_set:
                return True

        return False


class Work(BaseModel):
    iswc = CharField(unique=True, null=True)  # iswc may sometimes be missing
    title = CharField()

    # we could have a per model comparison that will take into account all fields and drill down into relations

    @property
    def providers(self):
        return Provider.select(Provider, WorkProvider).join(WorkProvider).where(WorkProvider.work == self.id)

    @property
    def contributors(self):
        return Contributor.select().join(WorkContributor).where(WorkContributor.work == self.id)

    def __str__(self):
        return f'{self.iswc} - {self.title}'


class Contributor(BaseModel):
    name = CharField(unique=True)

    def __str__(self):
        return f'{self.name}'


class WorkContributor(BaseModel):
    work = ForeignKeyField(Work, on_delete='CASCADE')
    contributor = ForeignKeyField(Contributor, on_delete='CASCADE')
    # maybe denormalize iswc here when too big


class Provider(BaseModel):
    name = CharField(unique=True)

    def __str__(self):
        return f'{self.name}'


class WorkProvider(BaseModel):
    work = ForeignKeyField(Work, on_delete='CASCADE')
    # unique together these? Meh, we can't trust the providers imports consistency...
    provider = ForeignKeyField(Provider, on_delete='CASCADE')
    provider_work_id = CharField(null=True)


MODELS = [Work, Contributor, WorkContributor, Provider, WorkProvider, ]


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
