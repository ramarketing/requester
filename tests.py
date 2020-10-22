import json
import pytest

import requester


@pytest.fixture
def client():
    return requester.app.test_client()


def test_invalid_method(client):
    resp = client.get('/')
    assert resp.status_code == 405


def test_incomplete(client):
    resp = client.post('/')
    assert resp.status_code == 400


def test_invalid(client):
    resp = client.post('/', json=dict(
        host='invalid.tld',
        url='https://invalid.tld'
    ))
    assert resp.status_code == 200
    resp = json.loads(resp.data)
    assert 'ip_address' in resp
    assert 'resolved_in' in resp
    assert 'content' in resp
    assert 'status_code' not in resp
    assert 'response_headers' not in resp
    assert 'elapsed' not in resp


def test_valid(client):
    resp = client.post('/', json=dict(
        host='github.com',
        url='https://github.com'
    ))
    assert resp.status_code == 200
    resp = json.loads(resp.data)
    assert 'ip_address' in resp
    assert 'resolved_in' in resp
    assert 'content' in resp
    assert 'status_code' in resp
    assert 'response_headers' in resp
    assert 'elapsed' in resp
