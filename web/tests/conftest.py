from datetime import datetime
import os
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from wsv import create_app


@pytest.fixture(scope='session')
def app():
    # FIXME when the app user will differ from postgres user this may not work anymore
    user = 'testing'
    password = 'testing'
    db = 'testing'
    con = psycopg2.connect(
        dbname='postgres',
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        cur.execute(f"DROP DATABASE {db} ;")
    except psycopg2.ProgrammingError:
        pass
    try:
        cur.execute(f"DROP USER {user} ;")
    except psycopg2.ProgrammingError:
        pass

    cur.execute(f"CREATE DATABASE {db} ;")
    cur.execute(f"CREATE USER {user} WITH ENCRYPTED PASSWORD '{password}';")
    cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db} TO {user};")
    con.close()

    app = create_app({
        'TESTING': True,
        'DATABASE': {
            'name': db,
            'engine': 'playhouse.pool.PostgresqlDatabase',
            'user': user,
            'password': password,
            'host': os.getenv('DATABASE_HOST'),
        },
    })
    with app.app_context():
        from wsv.db import create_tables
        create_tables()

    # TODO monkeypatch wsv.db.datetime.utcnow() so we'll be able to control chronology in tests

    yield app

    with app.app_context():
        from wsv.db import db_wrapper
        db_wrapper.database.close()
    con = psycopg2.connect(
        dbname='postgres',
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute(f"DROP DATABASE {db} ;")
    cur.execute(f"DROP USER {user} ;")
    con.close()


@pytest.fixture
def db_basic(app):
    with app.app_context():
        from wsv.db import (
            db_wrapper,
            Work,
            WorkContributor,
            Contributor,
            WorkProvider,
            Provider,
        )

        now = datetime.utcnow()
        w1 = Work(
            created=now,
            title="cde",
            iswc='xyz',
        )
        w1.save()

        c1 = Contributor(
            created=now,
            name='Contributor 1',
        )
        c1.save()
        WorkContributor(
            created=now,
            work=w1,
            contributor=c1,
        ).save()

        c2 = Contributor(
            created=now,
            name='Contributor 2',
        )
        c2.save()
        WorkContributor(
            created=now,
            work=w1,
            contributor=c2
        ).save()

        p1 = Provider(
            created=now,
            name='Provider 1',
        )
        p1.save()
        WorkProvider(
            created=now,
            work=w1,
            provider=p1,
            provider_work_id='x'
        ).save()

        # An already existing provider. Not related to any work yet
        p2 = Provider(
            created=now,
            name='sony',
        )
        p2.save()

        db_wrapper.database.close()
        yield app, (w1,), (c1, c2), (p1,p2)

        Provider.delete().execute()
        Work.delete().execute()
        Contributor.delete().execute()


@pytest.fixture
def client(db_basic):
    app, _, _, _ = db_basic
    return app.test_client()
