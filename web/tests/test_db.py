
def test_db_basic(db_work):
    app, works = db_work
    (w1, ) = works

    with app.app_context():
        from wsv.db import Work
        w1_again = Work.get(Work.id == w1.id)
        assert w1_again.title == w1.title
