import os
import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    provider_id = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    avatar_url = db.Column(db.String(500))
    
    __table_args__ = (db.UniqueConstraint('provider', 'provider_id', name='_provider_user_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'provider': self.provider,
            'provider_id': self.provider_id,
            'name': self.name,
            'email': self.email,
            'avatar_url': self.avatar_url
        }

class Friendship(db.Model):
    __tablename__ = 'friendships'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

class SharedUrl(db.Model):
    __tablename__ = 'shared_urls'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    url = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'sender_name': self.sender.name if self.sender else 'Unknown',
            'receiver_name': self.receiver.name if self.receiver else 'Unknown'
        }

with app.app_context():
    db.create_all()

@app.route('/api/users/auth', methods=['POST'])
def auth_user():
    data = request.json
    provider = data.get('provider')
    provider_id = data.get('provider_id')
    
    if not provider or not provider_id:
        return jsonify({'error': 'Missing provider info'}), 400

    user = User.query.filter_by(provider=provider, provider_id=provider_id).first()
    
    if not user:
        user = User(
            provider=provider,
            provider_id=provider_id,
            name=data.get('name'),
            email=data.get('email'),
            avatar_url=data.get('avatar_url')
        )
        db.session.add(user)
        db.session.commit()
    
    return jsonify(user.to_dict())

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/users/<int:user_id>/friends', methods=['GET'])
def get_friends(user_id):
    # Query friendships where user_id matches
    friend_ids = [f.friend_id for f in Friendship.query.filter_by(user_id=user_id).all()]
    friends = User.query.filter(User.id.in_(friend_ids)).all()
    return jsonify([f.to_dict() for f in friends])

@app.route('/api/users/<int:user_id>/history', methods=['GET'])
def get_history(user_id):
    history = SharedUrl.query.filter(
        (SharedUrl.sender_id == user_id) | (SharedUrl.receiver_id == user_id)
    ).order_by(SharedUrl.timestamp.desc()).all()
    return jsonify([h.to_dict() for h in history])

@app.route('/api/friendships', methods=['POST'])
def add_friendship():
    data = request.json
    user_id = data.get('user_id')
    friend_id = data.get('friend_id')
    
    if not user_id or not friend_id:
        return jsonify({'error': 'Missing IDs'}), 400
        
    try:
        # Check if exists
        exists = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first()
        if not exists:
            db.session.add(Friendship(user_id=user_id, friend_id=friend_id))
            db.session.add(Friendship(user_id=friend_id, friend_id=user_id))
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        
    return jsonify({'status': 'ok'}), 201

@app.route('/api/shares', methods=['POST'])
def share_url():
    data = request.json
    sender_id = data.get('sender_id')
    friend_ids = data.get('friend_ids')
    url = data.get('url')
    
    if not sender_id or not friend_ids or not url:
        return jsonify({'error': 'Missing data'}), 400

    try:
        for fid in friend_ids:
            share = SharedUrl(sender_id=sender_id, receiver_id=fid, url=url)
            db.session.add(share)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        
    return jsonify({'status': 'ok'}), 201

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    app.run(host=host, port=port, debug=debug)
