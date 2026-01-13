import pytest
from backend.app import db, User, Friendship

def test_friendship_creation(client):
    """Test that creating a friendship updates the database bi-directionally."""
    # Create two users
    u1 = User(provider='test', provider_id='1', name='User One', email='u1@test.com')
    u2 = User(provider='test', provider_id='2', name='User Two', email='u2@test.com')
    db.session.add_all([u1, u2])
    db.session.commit()
    
    # Create friendship
    resp = client.post('/api/friendships', json={
        'user_id': u1.id,
        'friend_id': u2.id
    })
    assert resp.status_code == 201
    
    # Verify DB state (bi-directional)
    f1 = Friendship.query.filter_by(user_id=u1.id, friend_id=u2.id).first()
    f2 = Friendship.query.filter_by(user_id=u2.id, friend_id=u1.id).first()
    
    assert f1 is not None
    assert f2 is not None

def test_share_url(client):
    """Test sharing a URL creates a record."""
    u1 = User(provider='test', provider_id='1', name='Sender', email='s@test.com')
    u2 = User(provider='test', provider_id='2', name='Receiver', email='r@test.com')
    db.session.add_all([u1, u2])
    db.session.commit()
    
    payload = {
        'sender_id': u1.id,
        'friend_ids': [str(u2.id)],
        'url': 'http://example.com'
    }
    
    resp = client.post('/api/shares', json=payload)
    assert resp.status_code == 201
    
    # Verify history
    hist_resp = client.get(f'/api/users/{u2.id}/history')
    data = hist_resp.json
    assert len(data) == 1
    assert data[0]['url'] == 'http://example.com'
    assert data[0]['sender_name'] == 'Sender'
