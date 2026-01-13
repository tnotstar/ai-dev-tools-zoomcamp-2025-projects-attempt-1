import pytest
import requests_mock
from flask import session

def test_dashboard_access_protected(client):
    """Verify unauthorized access to dashboard renders landing page or specific content."""
    # Without session, should render landing page
    resp = client.get('/')
    assert b"Get Started" in resp.data
    assert b"Share Effortlessly" in resp.data

def test_auth_flow_mock(client):
    """Mock a session and verify access to dashboard."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    with requests_mock.Mocker() as m:
        # Mock backend user fetch
        m.get('http://mock-backend/api/users/1', json={
            'id': 1, 'name': 'Test User', 'avatar_url': None
        })
        m.get('http://mock-backend/api/users/1/friends', json=[])
        m.get('http://mock-backend/api/users/1/history', json=[])
        
        resp = client.get('/')
        assert resp.status_code == 200
        assert b"Test User" in resp.data
        assert b"Sign Out" in resp.data

def test_htmx_share_url(client):
    """Test POST request to share URL returns HTML fragment."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        
    with requests_mock.Mocker() as m:
        # Mock backend share API
        m.post('http://mock-backend/api/shares', status_code=201)
        # Mock backend user fetch for friend name (used in response construction)
        m.get('http://mock-backend/api/users/2', json={'name': 'Friend User'})
        
        resp = client.post('/api/share', data={
            'url': 'http://cool-link.com',
            'friends': ['2']
        })
        
        assert resp.status_code == 200
        # Check for HTML fragment structure
        assert b'<div class="flex flex-col' in resp.data
        assert b'http://cool-link.com' in resp.data
        assert b'Friend User' in resp.data

def test_invite_friend_logic_frontend(client):
    """Test visiting invite link functionality (frontend side)."""
    with requests_mock.Mocker() as m:
        # Case 1: Not logged in -> Store pending_invite_sender and redirect to signup
        resp = client.get('/invite/accept/123')
        assert resp.status_code == 302
        assert '/signup' in resp.location
        with client.session_transaction() as sess:
            assert sess['pending_invite_sender'] == 123
            
        # Case 2: Logged in -> Call backend to create friendship
        with client.session_transaction() as sess:
            sess['user_id'] = 456
        
        m.post('http://mock-backend/api/friendships', status_code=201)
        
        resp = client.get('/invite/accept/123')
        assert resp.status_code == 302
        assert '/' == resp.location  # Redirects to home
        
        # Verify backend call was made
        assert m.called
        assert m.last_request.json() == {'user_id': 456, 'friend_id': 123}
