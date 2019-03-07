import csv
from dataclasses import dataclass, InitVar
from datetime import datetime
import click
from pathlib import Path

from flask.cli import with_appcontext
from peewee import *

from .db import (
    db_wrapper,
    Contributor,
    Work,
    WorkContributor,
    Provider,
    WorkProvider,
)
from .serializer import particular_schema


class CsvData:
    def import_csv(self, path):
        with open(path) as csvfile:
            # TODO detect files without the columns stated on the first row; they need to use cls.fields
            # TODO one time check if row.keys() match cls.fields
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_data, errors = self.schema.load(row)
                self.merge(row_data)

    def export_csv(self):
        pass


class ParticularCsvData(CsvData):
    fields = ['title', 'contributors', 'iswc', 'source', 'id']
    schema = particular_schema

    def merge(self, data):
        if not data['iswc']:
            # TODO attempt some fuzzy matching by work title
            return
        else:
            prefetch_queries = []
            works = Work.select().where(Work.iswc == data['iswc'])
            prefetch_queries.append(works)

        if data['source']:
            work_providers = WorkProvider.select()
            providers = Provider.select().where(Provider.name == data['source'])
            prefetch_queries.append(work_providers)
            prefetch_queries.append(providers)
        if data['contributors']:
            work_contributors = WorkContributor.select()
            contributors = Contributor.select()
            prefetch_queries.append(work_contributors)
            prefetch_queries.append(contributors)

        with db_wrapper.database.atomic():
            # TODO a lot of code in one place
            # FIXME in case of fuzzy matching this may be greater than 1
            work = prefetch(*prefetch_queries)
            assert len(work) <= 1

            now = datetime.utcnow()
            if work:
                work = work[0]
                if work.better_field('title', data['title']):
                    work.title = data['title']
                    work.save()
                if data['contributors'] and len(work.workcontributor_set):
                    # TODO use fuzz here too so we may upgrade our info on existing authors
                    current_contributors = { wc.contributor.name for wc in work.workcontributor_set }
                    for contrib in data['contributors']:
                        if contrib not in current_contributors:
                            c, _ = Contributor.get_or_create(
                                name=contrib,
                                defaults={'created': now},
                            )
                            WorkContributor(
                                created=now,
                                work=work,
                                contributor=c,
                            ).save()
                if data['source'] and len(work.workprovider_set):
                    current_providers = { wp.provider.name for wp in work.workprovider_set }
                    if data['source'] not in current_providers:
                        p, _ = Provider.get_or_create(
                            name=data['source'],
                            defaults={'created': now},
                        )
                        WorkProvider(
                            created=now,
                            work=work,
                            provider=p,
                            provider_work_id=data['id'],
                        ).save()
            else:
                w = Work(
                    created=now,
                    iswc=data['iswc'],
                    title=data['title'],
                )
                w.save()
                if data['source']:
                    p, _ = Provider.get_or_create(
                        name=data['source'],
                        defaults={'created': now},
                    )
                    wp = WorkProvider(
                        created=now,
                        work=w,
                        provider=p,
                        provider_work_id=data['id'],
                    )
                    wp.save()

                for contrib in data['contributors']:
                    c, _ = Contributor.get_or_create(
                        name=contrib,
                        defaults={'created': now},
                    )
                    wc = WorkContributor(
                        created=now,
                        work=w,
                        contributor=c,
                    )
                    wc.save()


csv_data = ParticularCsvData()


@click.command('import-csv')
@click.option('-f', '--file', required=True, type=Path)
@with_appcontext
def import_csv_command(file):
    if file.exists():
        wn = Work.select().count()
        cn = Contributor.select().count()
        pn = Provider.select().count()

        csv_data.import_csv(file)

        print(f'{Work.select().count() - wn} new works')
        print(f'{Contributor.select().count() - cn} new contributors')
        print(f'{Provider.select().count() - pn} new providers')
        # TODO better reporting
        print('Updates are not reported')
    else:
        print(f'file {file} not found')


def init_app(app):
    app.cli.add_command(import_csv_command)
