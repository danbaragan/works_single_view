from datetime import datetime, timedelta

from peewee import IntegrityError
import pytest
from wsv.db import (
    db_wrapper,
    Contributor,
    Work,
    WorkContributor,
    Provider,
    WorkProvider,
)


def test_db_basic(db_basic):
    app, works, _, _ = db_basic
    (w1, ) = works

    with app.app_context():
        w1_again = Work.get(Work.id == w1.id)
        assert w1_again.title == w1.title


@pytest.fixture
def db_works(app):
    with app.app_context():
        now = datetime.utcnow()
        w1 = Work(
            created=now,
            iswc='T000',
            title='Title with iswc',
        )
        w1.save()
        w2 = Work(
            created=now - timedelta(milliseconds=100),
            iswc=None,
            title='Title without iswc',
        )
        w2.save()
        w3 = Work(
            created=now - timedelta(milliseconds=200),
            iswc=None,
            title='Another Title without iswc',
        )
        w3.save()

        db_wrapper.database.close()
        yield app, (w1, w2, w3)

        Work.delete().execute()


def test_work_get_iswc_missing(db_works):
    app, works = db_works
    with app.app_context():
        no_iswc = Work.select().where(Work.iswc.is_null(True))
        assert no_iswc.count() == 2


def test_work_duplicate_iswc(db_works):
    app, works = db_works
    iswc = works[0].iswc
    with app.app_context():
        w = Work(
            created=datetime.utcnow(),
            title='Reject this',
            iswc=iswc,
        )
        with db_wrapper.database.atomic() as tr:
            with pytest.raises(IntegrityError):
                w.save()
            tr.rollback()


@pytest.fixture
def db_contributors(db_works):
    app, works = db_works
    w1, w2, w3 = works
    with app.app_context():
        now = datetime.utcnow()
        c1 = Contributor(
            created=now,
            name='Author 1',
        )
        c1.save()
        WorkContributor(
            created=now,
            work=w1,
            contributor=c1,
        ).save()
        # c1 contributed to 2 works
        WorkContributor(
            created=now,
            work=w2,
            contributor=c1,
        ).save()

        # w2 has 2 authors
        c2 = Contributor(
            created=now - timedelta(milliseconds=100),
            name='Author 2'
        )
        c2.save()
        WorkContributor(
            created=now - timedelta(milliseconds=100),
            work=w2,
            contributor=c2,
        ).save()

        db_wrapper.database.close()
        yield app, works, (c1, c2)

        Contributor.delete().execute()


def test_work_contributors_delete(db_contributors):
    app, works, contribs = db_contributors
    w1, w2, w3 = works
    c1, c2 = contribs
    with app.app_context():
        Contributor.delete().where(Contributor.id == c1.id).execute()
        w1_count = WorkContributor.select().where(WorkContributor.work == w1.id).count()
        assert w1_count == 0
        w2_count = WorkContributor.select().where(WorkContributor.work == w2.id).count()
        # The connection between w2 and c2 still exists, after c1 delete
        assert w2_count == 1


@pytest.fixture
def db_providers(db_works):
    app, works = db_works
    w1, w2, w3 = works
    with app.app_context():
        now = datetime.utcnow()
        p1 = Provider(
            created=now,
            name='Provider 1',
        )
        p1.save()
        WorkProvider(
            created=now,
            work=w1,
            provider=p1,
            provider_specific_id='1',
        ).save()
        WorkProvider(
            created=now - timedelta(milliseconds=100),
            work=w2,
            provider=p1,
            provider_specific_id='2',
        ).save()

        p2 = Provider(
            created=now,
            name='Provider 2',
        )
        p2.save()
        WorkProvider(
            created=now,
            work=w2,
            provider=p2,
            provider_specific_id='x',
        ).save()

        db_wrapper.database.close()
        yield app, works, (p1, p2)

        Provider.delete().execute()


# Because pytest is so cool...
def test_fixture_two_uses_one_instance(db_contributors, db_providers):
    app, works, contributors = db_contributors
    app, works2, providers = db_providers

    assert works[0].id == works2[0].id


def test_providers_delete(db_providers):
    app, works, providers = db_providers
    p1, p2 = providers
    w1, w2, w3 = works
    with app.app_context():
        # one provider, p1, to this work.
        count1 = WorkProvider.select().where(WorkProvider.work == w1.id).count()
        assert count1 == 1
        # 2 providers, p1 and p2, for this work
        count2 = WorkProvider.select().where(WorkProvider.work == w2.id).count()
        assert count2 == 2

        Provider.delete().where(Provider.id == p1.id).execute()
        # p1 delete cascades
        count1 = WorkProvider.select().where(WorkProvider.work == w1.id).count()
        assert count1 == 0
        count2 = WorkProvider.select().where(WorkProvider.work == w2.id).count()
        assert count2 == 1
