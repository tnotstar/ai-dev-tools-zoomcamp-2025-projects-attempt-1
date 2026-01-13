import os
import requests
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['SESSION_COOKIE_NAME'] = 'poshbullet-session'

# Backend Config
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8081')

# OAuth Setup
oauth = OAuth(app)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid profile email'}
    )

FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')

if FACEBOOK_CLIENT_ID and FACEBOOK_CLIENT_SECRET:
    oauth.register(
        name='facebook',
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        api_base_url='https://graph.facebook.com/v18.0/',
        access_token_url='https://graph.facebook.com/v18.0/oauth/access_token',
        authorize_url='https://www.facebook.com/v18.0/dialog/oauth',
        client_kwargs={'scope': 'email'}
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('signup'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        try:
            r = requests.get(f"{BACKEND_URL}/api/users/{session['user_id']}")
            if r.status_code == 200:
                user = r.json()
            elif r.status_code == 404:
                # Session exists but user not in DB (likely DB reset). Logout.
                session.clear()
                return redirect(url_for('index'))
            
            friends_resp = requests.get(f"{BACKEND_URL}/api/users/{session['user_id']}/friends")
            friends = friends_resp.json() if friends_resp.status_code == 200 else []

            hist_resp = requests.get(f"{BACKEND_URL}/api/users/{session['user_id']}/history")
            history = hist_resp.json() if hist_resp.status_code == 200 else []
            
            return render_template('index.html', user=user, friends=friends, history=history)
        except requests.RequestException as e:
            print(f"Backend connection failed: {e}")
            return "Error connecting to backend service", 503
            
    return render_template('index.html', user=None)

@app.route('/signup')
def signup():
    if 'user_id' in session:
        return redirect(url_for('index'))
    val = request.args.get('message')
    return render_template('signup.html', message=val)

@app.route('/auth/login/<provider>')
def login(provider):
    if provider == 'google' and not GOOGLE_CLIENT_ID:
        return redirect(url_for('auth_callback', provider=provider, mock='true'))
    if provider == 'facebook' and not FACEBOOK_CLIENT_ID:
        return redirect(url_for('auth_callback', provider=provider, mock='true'))
    redirect_uri = url_for('auth_callback', provider=provider, _external=True)
    return oauth.create_client(provider).authorize_redirect(redirect_uri)

@app.route('/auth/callback/<provider>')
def auth_callback(provider):
    if request.args.get('mock') == 'true':
        user_info = {
            'sub': f'mock_{provider}_12345',
            'name': f'Mock {provider.capitalize()} User',
            'email': f'user@{provider}.mock',
            'picture': f'https://ui-avatars.com/api/?name={provider}'
        }
    else:
        client = oauth.create_client(provider)
        token = client.authorize_access_token()
        if provider == 'google':
            user_info = token.get('userinfo') or client.userinfo()
        elif provider == 'facebook':
            resp = client.get('me?fields=id,name,email,picture')
            data = resp.json()
            user_info = {
                'sub': data['id'],
                'name': data['name'],
                'email': data.get('email'),
                'picture': data['picture']['data']['url'] if 'picture' in data else None
            }
    
    payload = {
        'provider': provider,
        'provider_id': user_info['sub'],
        'name': user_info['name'],
        'email': user_info.get('email'),
        'avatar_url': user_info.get('picture')
    }
    
    try:
        r = requests.post(f"{BACKEND_URL}/api/users/auth", json=payload)
        r.raise_for_status()
        user_data = r.json()
        session['user_id'] = user_data['id']
        
        invite_sender_id = session.pop('pending_invite_sender', None)
        if invite_sender_id and invite_sender_id != user_data['id']:
            requests.post(f"{BACKEND_URL}/api/friendships", json={
                'user_id': user_data['id'],
                'friend_id': invite_sender_id
            })

    except Exception as e:
        print(f"Auth failed: {e}")
        return "Authentication via backend failed", 500
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/invite/generate')
@login_required
def generate_invite():
    invite_link = url_for('handle_invite', inviter_id=session['user_id'], _external=True)
    return render_template('invite.html', invite_link=invite_link)

@app.route('/invite/accept/<int:inviter_id>')
def handle_invite(inviter_id):
    if 'user_id' in session:
        if session['user_id'] == inviter_id:
             return "You cannot invite yourself.", 400
        
        try:
            requests.post(f"{BACKEND_URL}/api/friendships", json={
                'user_id': session['user_id'],
                'friend_id': inviter_id
            })
        except:
            pass
        return redirect(url_for('index'))
    else:
        session['pending_invite_sender'] = inviter_id
        return redirect(url_for('signup', message="Please sign in to accept the invitation.") )

@app.route('/api/share', methods=['POST'])
@login_required
def share_url():
    url = request.form.get('url')
    friend_ids = request.form.getlist('friends')
    
    if not url or not friend_ids:
        return "Missing URL or friends", 400

    try:
        payload = {
            'sender_id': session['user_id'],
            'friend_ids': friend_ids,
            'url': url
        }
        r = requests.post(f"{BACKEND_URL}/api/shares", json=payload)
        r.raise_for_status()

        new_items_html = ""
        for fid in friend_ids:
             f_resp = requests.get(f"{BACKEND_URL}/api/users/{fid}")
             friend_data = f_resp.json()
             receiver_name = friend_data['name']
             
             new_items_html += f'''
                <div class="flex flex-col p-4 rounded-xl mb-3 border-l-4 border-indigo-500 bg-indigo-500/10 fade-in">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs font-bold text-slate-400">Just now</span>
                        <span class="text-xs px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-white/5">
                            You &rarr; {receiver_name}
                        </span>
                    </div>
                    <a href="{url}" target="_blank" class="text-blue-400 font-medium truncate">{url}</a>
                </div>
             '''
        return new_items_html

    except Exception as e:
        print(f"Share failed: {e}")
        return "Error sharing URL", 500

@app.route('/api/history_partial')
@login_required
def history_partial():
     try:
        hist_resp = requests.get(f"{BACKEND_URL}/api/users/{session['user_id']}/history")
        history = hist_resp.json() if hist_resp.status_code == 200 else []
        
        html = ""
        for item in history:
            user_id = session['user_id']
            is_me = (item['sender_id'] == user_id)
            direction = "You sent to" if is_me else "sent you"
            other_person = item['receiver_name'] if is_me else item['sender_name']
            style = "border-l-4 border-indigo-500 bg-indigo-500/10" if is_me else "border-l-4 border-emerald-500 bg-emerald-500/10"
            
            html += f'''
            <div class="flex flex-col p-4 rounded-xl mb-3 {style} hover:bg-white/5 transition-colors">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-xs font-bold text-slate-400">{item['timestamp']}</span>
                    <span class="text-xs px-3 py-1 rounded-full border border-white/5 {'bg-indigo-500/20 text-indigo-300' if is_me else 'bg-emerald-500/20 text-emerald-300'}">
                        {direction} {other_person}
                    </span>
                </div>
                <a href="{item['url']}" target="_blank" class="text-blue-400 hover:text-blue-300 font-medium truncate py-1 block flex items-center gap-2">
                   {item['url']}
                </a>
            </div>
            '''
        return html
     except:
         return "Error loading history"

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    app.run(host=host, port=port, debug=debug)
