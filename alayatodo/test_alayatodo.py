import os
import tempfile

import pytest

from alayatodo import app
from main import init_db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQL_ALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    client = app.test_client()

    with app.app_context():
        init_db()

    yield client


def test_home_endpoint(client):
    rv = client.get('/')
    assert 200 is rv.status_code


def test_login_logout_happy_path(client):
    rv = login(client, 'user1', 'user1')
    assert b'user1 Logout</a>' in rv.data
    assert b'<a href="/login">Login</a>' not in rv.data
    assert b'Vivamus tempus' in rv.data
    assert 200 is rv.status_code

    rv = logout(client)
    assert b'user1 Logout</a>' not in rv.data
    assert b'<a href="/login">Login</a>' in rv.data
    assert 200 is rv.status_code


def test_login_logout_sad_path(client):
    rv = login(client, '1user', 'user1')
    assert b'1user Logout</a>' not in rv.data
    assert b'<a href="/login">Login</a>' in rv.data
    assert 200 is rv.status_code

    rv = login(client, 'user1', 'user2')
    assert b'user1 Logout</a>' not in rv.data
    assert b'<a href="/login">Login</a>' in rv.data
    assert 200 is rv.status_code

    rv = login(client, 'user12', 'user12')
    assert b'user12 Logout</a>' not in rv.data
    assert b'<a href="/login">Login</a>' in rv.data
    assert 200 is rv.status_code


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)
