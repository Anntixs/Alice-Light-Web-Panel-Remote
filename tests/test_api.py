import os
os.environ['ALICE_PANEL_TOKEN']='test-secret'
from fastapi.testclient import TestClient
from backend.app import app
client=TestClient(app)
H={'X-Panel-Token':'test-secret'}

def test_auth_and_mock():
    assert client.get('/api/status').status_code==401
    r=client.get('/api/status',headers=H)
    assert r.status_code==200
    assert r.json()['mode']=='mock'

def test_unsupported_controls():
    assert client.post('/api/player/control',headers=H,json={'action':'play'}).status_code==501
    assert client.post('/api/lighting',headers=H,json={}).status_code==501
