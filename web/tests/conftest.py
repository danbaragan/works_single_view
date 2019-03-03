from datetime import datetime, timedelta
import os
import pytest

from wsv import create_app


@pytest.fixture(scope='session')
def app(tmp_path_factory):
    # TODO open this in memory
    db_path = tmp_path_factory.mktemp('db') / os.getenv('DATABASE_URL', 'test.db')
    app = create_app({
        'TESTING': True,
        'DATABASE': {
            'name': db_path,
            'engine': 'playhouse.pool.SqliteDatabase',
        },
    })
    with app.app_context():
        from wsv.db import create_tables
        create_tables()

    yield app

    with app.app_context():
        from wsv.db import drop_tables
        drop_tables


@pytest.fixture
def db_work(app):
    with app.app_context():
        from wsv.db import db_wrapper, Work

        now = datetime.utcnow()
        w1 = Work(
            created=now,
            modified=now,
            title="Work 1",
        )
        w1.save()

        db_wrapper.database.close()
        yield app, (w1,)


@pytest.fixture
def client(db_work):
    app, _ = db_work
    return app.test_client()
