from datetime import datetime

import pytest
from unittest import mock

from wsv.importer import csv_data
from wsv.db import (
    db_wrapper,
    Contributor,
    Work,
    WorkContributor,
    Provider,
    WorkProvider,
)


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
    count = 1

    with app.app_context():
        c = 0
        with open(csv_file_simple_new) as f:
            c = csv_data.import_csv(f)

        assert count == c
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
    count = 1

    with app.app_context():
        c = 0
        with open(csv_file_simple_existing) as f:
            c = csv_data.import_csv(f)
        assert count == c
    # does not crash


def test_importer_single_complete_row_existing(db_basic, csv_file_simple_existing):
    app, works, contribs, provs = db_basic
    # db_basic already has iswc 'xyz'
    w1 = works[0]
    e_title = 'abc cde'
    e_iswc = 'xyz'
    e_contribs = {'Obispo Pascal Michel', 'Florence Lionel Jacques'}
    e_prov = 'sony'
    count = 1

    # the default situation in db_basic
    assert w1.iswc == e_iswc
    assert w1.title != e_title
    assert w1.workprovider_set.count() == 1
    assert w1.workcontributor_set.count() == 2

    with app.app_context():
        c = 0
        with open(csv_file_simple_existing) as f:
            c = csv_data.import_csv(f)

        assert count == c
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
    count = 2

    with app.app_context():
        c = 0
        with open(csv_file_contrib_overlap_new) as f:
            c = csv_data.import_csv(f)
        assert count == c
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
    count = 8

    with app.app_context():
        c = 0
        with open(csv_file_all) as f:
            c = csv_data.import_csv(f)

        assert c == count
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


@mock.patch('wsv.importer.csv_data.merge')
def test_csv_import_schema(merge, csv_file_simple_new):
    count = 1
    c = 0
    with open(csv_file_simple_new) as f:
        c = csv_data.import_csv(f)

    assert count == c
    assert merge.call_count == 1
    arg = merge.call_args[0][0]
    assert list(arg['contributors']) == ['O Brien Edward John', 'Yorke Thomas Edward', 'Greenwood Colin Charles']
    assert arg['iswc'] == 'T0101974597'
    assert arg['title'] == 'Adventure of a Lifetime'
    assert arg['source'] == 'warner'
    assert arg['id'] == '2'


def test_export(db_basic, tmp_path):
    path = tmp_path / 'test.csv'
    app, works, _, _ = db_basic
    # FIXME unorderd results
    expected = """title,contributors,iswc,source,id
cde,Contributor 1|Contributor 2,xyz,sony,y
cde,Contributor 1|Contributor 2,xyz,Provider 1,x
"""
    with app.app_context():
        p2 = Provider.get(Provider.name == 'sony')
        WorkProvider.create(
            created=datetime.utcnow(),
            work=works[0],
            provider=p2,
            provider_work_id='y',
        )
        with open(path, "w") as f:
            csv_data.export_csv(f)

        assert path.read_text() == expected
