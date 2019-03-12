from flask import current_app
import pytest


@pytest.mark.parametrize('url_in,bytes_out', [
    ('', b"Hello world!"),
    ('dan', b"Hello dan!"),
])
def test_hello(client, url_in, bytes_out):
    assert current_app.testing
    response = client.get(f'/hello/{url_in}')
    assert bytes_out in response.data
