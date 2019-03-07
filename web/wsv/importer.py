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


@dataclass
class CsvItem:
    # TODO sanitize this! Can we use marshmallow?
    # TODO decouple merge - different providers will have differnt formats. Merge logic should be the same
    title: str = ''
    contributors: InitVar[str] = ''
    contributor_list: list = None
    iswc: str = ''
    source: str = ''
    id: str = ''

    def __post_init__(self, contributors):
        self.contributor_list = [ c for c in contributors.split('|') if c ]

    def merge(self):
        if not self.iswc:
            # TODO attempt some fuzzy matching by work title
            return
        else:
            prefetch_queries = []
            works = Work.select().where(Work.iswc == self.iswc)
            prefetch_queries.append(works)

        if self.source:
            work_providers = WorkProvider.select()
            providers = Provider.select().where(Provider.name == self.source)
            prefetch_queries.append(work_providers)
            prefetch_queries.append(providers)
        if self.contributor_list:
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
                if work.better_field('title', self.title):
                    work.title = self.title
                    work.save()
                if self.contributor_list and len(work.workcontributor_set):
                    # TODO use fuzz here too so we may upgrade our info on existing authors
                    current_contributors = { wc.contributor.name for wc in work.workcontributor_set }
                    for contrib in self.contributor_list:
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
                if self.source and len(work.workprovider_set):
                    current_providers = { wp.provider.name for wp in work.workprovider_set }
                    if self.source not in current_providers:
                        p, _ = Provider.get_or_create(
                            name=self.source,
                            defaults={'created': now},
                        )
                        WorkProvider(
                            created=now,
                            work=work,
                            provider=p,
                            provider_work_id=self.id,
                        ).save()
            else:
                w = Work(
                    created=now,
                    iswc=self.iswc,
                    title=self.title,
                )
                w.save()
                if self.source:
                    p, _ = Provider.get_or_create(
                        name=self.source,
                        defaults={'created': now},
                    )
                    wp = WorkProvider(
                        created=now,
                        work=w,
                        provider=p,
                        provider_work_id=self.id,
                    )
                    wp.save()

                for contrib in self.contributor_list:
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


# a single function should suffice for now
def import_csv(path):
    with open(path) as csvfile:
        # TODO files without the columns stated on the first row will not behave
        reader = csv.DictReader(csvfile)
        for row in reader:
            CsvItem(**row).merge()


@click.command('import-csv')
@click.option('-f', '--file', required=True, type=Path)
@with_appcontext
def import_csv_command(file):
    if file.exists():
        wn = Work.select().count()
        cn = Contributor.select().count()
        pn = Provider.select().count()

        import_csv(file)

        print(f'{Work.select().count() - wn} new works')
        print(f'{Contributor.select().count() - cn} new contributors')
        print(f'{Provider.select().count() - pn} new providers')
        # TODO better reporting
        print('Updates are not reported')
    else:
        print(f'file {file} not found')


def init_app(app):
    app.cli.add_command(import_csv_command)
