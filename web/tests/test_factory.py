from flask import current_app
import pytest


@pytest.mark.skip("This does very bad things to our session scoped app fixture")
def test_config():
    from wsv import create_app
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    assert current_app.testing
    response = client.get('/hello')
    assert response.data == b"Hello world!"
