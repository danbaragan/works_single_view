import pytest

from wsv.importer import import_csv, CsvItem
from wsv.db import (
    db_wrapper,
    Contributor,
    Work,
    WorkContributor,
    Provider,
    WorkProvider,
)


def test_csvitem_all_missing_ok(app):
    row = dict()
    c = CsvItem(**row)
    assert c.title == ''
    assert c.contributor_list == []
    assert c.iswc == ''
    assert c.source == ''
    assert c.id == ''


def test_csvitem_all_ok(app):
    row = dict(
        title='Shape of You',
        contributors='Edward Sheeran',
        iswc='T9204649558',
        source='warner',
        id='1',
    )
    c = CsvItem(**row)
    assert c.title == 'Shape of You'
    assert c.contributor_list == ['Edward Sheeran']
    assert c.iswc == 'T9204649558'
    assert c.source == 'warner'
    assert c.id == '1'


def test_csvitem_contrib_aggregate_ok(app):
    row = dict(
        title='Shape of You',
        contributors='Edward Sheeran|bla bla',
        iswc='T9204649558',
        source='warner',
        id='1',
    )
    c = CsvItem(**row)
    assert c.title == 'Shape of You'
    assert c.contributor_list == ['Edward Sheeran', 'bla bla']
    assert c.iswc == 'T9204649558'
    assert c.source == 'warner'
    assert c.id == '1'


@pytest.fixture(scope='session')
def csv_file_simple_new(tmp_path_factory):
    content = """title,contributors,iswc,source,id
Adventure of a Lifetime,O Brien Edward John|Yorke Thomas Edward|Greenwood Colin Charles,T0101974597,warner,2
"""
    path = tmp_path_factory.mktemp("csv") / 'works_meta_simple.csv'
    path.write_text(content)

    yield path


def test_importer_single_complete_row_new(db_basic, csv_file_simple_new):
    app, _, _, _ = db_basic
    e_title = 'Adventure of a Lifetime'
    e_iswc = 'T0101974597'
    e_contrib = {'O Brien Edward John', 'Yorke Thomas Edward', 'Greenwood Colin Charles'}
    e_prov = 'warner'
    e_prov_id = '2'

    with app.app_context():
        import_csv(csv_file_simple_new)
        w = Work.select().where(Work.iswc == e_iswc)
        assert w.count() == 1
        w = w[0]
        assert w.title == e_title
        assert w.iswc == e_iswc

        assert w.workprovider_set.count() == 1
        wp = w.workprovider_set[0]
        assert wp.provider.name == e_prov
        assert wp.provider_work_id == e_prov_id

        assert w.workcontributor_set.count() == 3
        contributors = { x.contributor.name for x in w.workcontributor_set }
        assert contributors == e_contrib


@pytest.fixture(scope='session')
def csv_file_simple_existing(tmp_path_factory):
    content = """title,contributors,iswc,source,id
abc cde,Obispo Pascal Michel|Florence Lionel Jacques,xyz,sony,3
"""
    path = tmp_path_factory.mktemp("csv") / 'works_meta_simple.csv'
    path.write_text(content)

    yield path


def test_importer_single_complete_row_mismatch_existing(db_basic, csv_file_simple_existing):
    app, _, _, _ = db_basic

    with app.app_context():
        import_csv(csv_file_simple_existing)
    # does not crash


def test_importer_single_complete_row_existing(db_basic, csv_file_simple_existing):
    app, works, contribs, provs = db_basic
    # db_basic already has iswc 'xyz'
    w1 = works[0]
    e_title = 'abc cde'
    e_iswc = 'xyz'
    e_contribs = {'Obispo Pascal Michel', 'Florence Lionel Jacques'}
    e_prov = 'sony'
    e_prov_id = '3'

    # the default situation in db_basic
    assert w1.iswc == e_iswc
    assert w1.title != e_title
    assert w1.workprovider_set.count() == 1
    assert w1.workcontributor_set.count() == 2

    with app.app_context():
        import_csv(csv_file_simple_existing)
        w = Work.select().where(Work.iswc == e_iswc)
        assert w.count() == 1
        w = w[0]
        assert w.title == e_title
        assert w.id == w1.id

        assert w.workcontributor_set.count() == 4
        contribs = { wc.contributor.name for wc in w.workcontributor_set }
        assert contribs > e_contribs

        assert w.workprovider_set.count() == 2
        provs = { wp.provider.name for wp in w.workprovider_set }
        assert e_prov in provs


@pytest.fixture(scope='session')
def csv_file_contrib_overlap_new(tmp_path_factory):
    content = """title,contributors,iswc,source,id
Adventure of a Lifetime,O Brien Edward John|Yorke Thomas Edward|Greenwood Colin Charles,T0101974597,warner,2
Adventure of a Lifetime,O Brien Edward John|Selway Philip James,T0101974597,warner,3
"""
    path = tmp_path_factory.mktemp("csv") / 'works_meta_simple.csv'
    path.write_text(content)

    yield path


def test_importer_contrib_overlap_new(db_basic, csv_file_contrib_overlap_new):
    app, works, contribs, provs = db_basic
    e_title = 'Adventure of a Lifetime'
    e_iswc = 'T0101974597'
    e_contribs = {'O Brien Edward John', 'Yorke Thomas Edward', 'Greenwood Colin Charles', 'Selway Philip James'}
    e_prov = 'warner'

    with app.app_context():
        import_csv(csv_file_contrib_overlap_new)
        w = Work.select().where(Work.iswc == e_iswc)
        assert w.count() == 1
        w = w[0]
        assert w.title == e_title

        assert w.workcontributor_set.count() == 4
        contribs = { wc.contributor.name for wc in w.workcontributor_set }
        assert contribs == e_contribs

        assert w.workprovider_set.count() == 1
        assert w.workprovider_set[0].provider.name == e_prov


@pytest.fixture(scope='session')
def csv_file_all(tmp_path_factory):
    content = """title,contributors,iswc,source,id
Shape of You,Edward Sheeran,T9204649558,warner,1
Shape of You,Edward Christopher Sheeran,T9204649558,sony,1
Adventure of a Lifetime,O Brien Edward John|Yorke Thomas Edward|Greenwood Colin Charles,T0101974597,warner,2
Adventure of a Lifetime,O Brien Edward John|Selway Philip James,T0101974597,warner,3
Me Enamoré,Rayo Gibo Antonio|Ripoll Shakira Isabel Mebarak,T9214745718,universal,1
Me Enamore,Rayo Gibo Antonio|Ripoll Shakira Isabel Mebarak,T9214745718,warner,4
Je ne sais pas,Obispo Pascal Michel|Florence Lionel Jacques,,sony,2
Je ne sais pas,Obispo Pascal Michel|Florence Lionel Jacques,T0046951705,sony,3
"""
    path = tmp_path_factory.mktemp("csv") / 'works_meta_all.csv'
    path.write_text(content)

    yield path


def test_importer_all(db_basic, csv_file_all):
    app, works, _, _ = db_basic

    with app.app_context():
        import_csv(csv_file_all)
        ws = Work.select()
        assert ws.count() == 5  # 4+1 the conftest work

        w = Work.select().where(Work.iswc == 'T9204649558')
        assert w.count() == 1
        w = w[0]
        assert w.title == 'Shape of You'
        # FIXME "Edward Christopher Sheeran" should replace "Edward Sheeran"
        assert w.workprovider_set.count() == 2

        w = Work.select().where(Work.iswc == 'T0101974597')
        assert w.count() == 1
        w = w[0]
        assert w.title == 'Adventure of a Lifetime'
        assert w.workcontributor_set.count() == 4
        assert w.workprovider_set.count() == 1

        w = Work.select().where(Work.iswc == 'T9214745718')
        assert w.count() == 1
        w = w[0]
        assert w.title == 'Me Enamoré'
        assert w.workcontributor_set.count() == 2
        assert w.workprovider_set.count() == 2

        # TODO don't ignore the iswc empty row, maybe it has useful info
        w = Work.select().where(Work.iswc == 'T0046951705')
        assert w.count() == 1
        w = w[0]

        assert w.title == 'Je ne sais pas'
        assert w.workcontributor_set.count() == 2
        assert w.workprovider_set.count() == 1
        assert w.workprovider_set[0].provider_work_id == '3'




