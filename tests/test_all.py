import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

def smoke_test(client):
    rv = client.get('/')
    assert b'No entries here so far' in rv.data