# AGENTS.md

Project-specific guidance for agents working in this codebase.

## Project Overview

**PoshBullet** is a collaborative URL sharing platform MVP built as a Python `uv` workspace with two Flask applications:
- **Backend**: REST API with SQLAlchemy ORM (port 5001)
- **Frontend**: Web interface with HTMX, TailwindCSS, and OAuth authentication (port 5000)

### Architecture
```
┌─────────────┐         HTTP         ┌─────────────┐
│  Frontend   │ ◄────────────────────► │  Backend   │
│  (Flask)    │    localhost:5001      │  (Flask)    │
│  Port 5000  │                         │  Port 5001  │
└─────────────┘                         └─────────────┘
     |                                          |
     ├─ Jinja2 Templates                        ├─ SQLAlchemy Models
     ├─ HTMX Interactions                       ├─ OpenAPI Spec
     ├─ OAuth (Google/FB/Mock)                  └─ REST API Endpoints
     └─ Session Management
```

## Essential Commands

### Start the full environment
```bash
python dev.py
```
This script:
1. Checks database status (uses in-memory SQLite by default)
2. Syncs dependencies for both backend and frontend via `uv sync`
3. Starts backend server on port 5001
4. Starts frontend server on port 5000
5. Monitors both processes (Ctrl+C to stop both)

### Individual workspace commands
```bash
# In root directory - manage workspace
uv sync

# In backend/ directory
uv sync                          # Sync backend dependencies
uv run app.py                    # Start backend server (port 5001)

# In frontend/ directory
uv sync                          # Sync frontend dependencies
uv run app.py                    # Start frontend server (port 5000)
```

### Environment configuration
Each subproject has its own `.env` file:

**Backend (backend/.env)**:
```
FLASK_APP=app.py
FLASK_DEBUG=0                   # Set to 1 for development
HOST=0.0.0.0
PORT=5001
DATABASE_URL=sqlite:///:memory:  # Change to file path for persistence
```

**Frontend (frontend/.env)**:
```
FLASK_APP=app.py
FLASK_DEBUG=0                   # Set to 1 for development
HOST=0.0.0.0
PORT=5000
BACKEND_URL=http://localhost:5001  # Frontend calls backend here
SECRET_KEY=dev_secret_key           # Session encryption (change in prod)
```

**Optional OAuth** (add to frontend/.env):
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
FACEBOOK_CLIENT_ID=your_client_id
FACEBOOK_CLIENT_SECRET=your_client_secret
```

**Note**: Mock OAuth is available when credentials are not set (see signup.html for developer mode links).

## Code Organization

### Workspace Structure
```
/workspaces/ai-dev-tools-zoomcamp-2025-projects-attempt-1/
├── dev.py                 # Main startup script (installs deps + runs both servers)
├── pyproject.toml         # Workspace configuration
├── .python-version        # Python version pinning (>=3.10)
├── backend/
│   ├── .env              # Backend configuration
│   ├── app.py            # Flask app with SQLAlchemy models + REST API
│   ├── openapi.yaml      # API specification
│   └── pyproject.toml    # Backend dependencies
└── frontend/
    ├── .env              # Frontend configuration
    ├── app.py            # Flask app with routes + OAuth + HTMX
    ├── pyproject.toml    # Frontend dependencies
    └── templates/
        ├── index.html    # Dashboard with HTMX interactions
        ├── signup.html   # OAuth sign-up page
        └── invite.html   # Invite link generation page
```

### Backend API (backend/app.py)

**Models** (lines 16-62):
- `User`: OAuth-based users with unique constraint on (provider, provider_id)
- `Friendship`: Bidirectional friendship relationships (two records per pair)
- `SharedUrl`: URL sharing history with sender/receiver/timestamp

**Key endpoints**:
- `POST /api/users/auth`: Authenticate or create user via OAuth
- `GET /api/users/<id>`: Get user details
- `GET /api/users/<id>/friends`: Get user's friend list
- `GET /api/users/<id>/history`: Get shared URL history (sent and received)
- `POST /api/friendships`: Create friendship (bidirectional)
- `POST /api/shares`: Share URL with multiple friends

### Frontend Routes (frontend/app.py)

**Session management**:
- `@login_required` decorator (line 45) protects routes
- Session stores `user_id` and `pending_invite_sender`

**Key routes**:
- `/`: Dashboard (shows landing or user dashboard based on auth state)
- `/signup`: Sign-up page with OAuth buttons
- `/auth/login/<provider>`: OAuth login initiation
- `/auth/callback/<provider>`: OAuth callback (handles mock and real OAuth)
- `/logout`: Clear session
- `/invite/generate`: Generate invite link
- `/invite/accept/<inviter_id>`: Accept friend invitation
- `POST /api/share`: Share URL with friends (returns HTML for HTMX)
- `GET /api/history_partial`: Refresh history (returns HTML for HTMX)

### HTMX Patterns

Frontend uses HTMX for dynamic updates without page reloads:

**Share form** (index.html:69):
```html
<form hx-post="/api/share"
      hx-target="#history-list"
      hx-swap="afterbegin"
      hx-indicator="#sending-indicator">
```
- POSTs to `/api/share`
- Inserts returned HTML at beginning of `#history-list`
- Shows spinner indicator during request

**Refresh history** (index.html:118):
```html
<button hx-get="/api/history_partial" hx-target="#history-list">
```
- Fetches fresh history HTML and replaces content

Backend returns HTML snippets directly (not JSON) for HTMX.

## Naming Conventions and Style

### Python/Flask
- Function names: `snake_case` for all functions, `PascalCase` for classes
- Route handlers: Descriptive names (`get_user`, `share_url`, `add_friendship`)
- Models: `PascalCase` with lowercase table names (`__tablename__ = 'users'`)
- Database columns: `snake_case`

### Frontend/Templates
- CSS classes: TailwindCSS utility classes
- Template variables: `snake_case` (`{{ user.name }}`, `{{ friend.id }}`)
- HTMX attributes: Lowercase with hyphens (`hx-post`, `hx-target`, `hx-swap`)

### Design Patterns
**Glass morphism**: Repeated use of `.glass` class for frosted glass effect:
```css
.glass {
    background: rgba(255, 255, 255, 0.05/0.7);
    backdrop-filter: blur(10px/20px);
    border: 1px solid rgba(255, 255, 255, 0.1/0.18);
}
```

**Gradient text**: Used for branding:
```html
<span class="bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500">
```

## Important Gotchas

### Database Persistence
- **Default**: In-memory SQLite (`sqlite:///:memory:`)
- **Lost on restart**: All data cleared when backend restarts
- **To persist**: Change `DATABASE_URL` in backend/.env to file path (e.g., `sqlite:///poshbullet.db`)

### Session Management
- Frontend sessions are server-side (Flask sessions)
- Sessions are tied to a single frontend instance
- Multiple frontend instances will have separate sessions
- Backend is stateless except for database

### OAuth Authentication
- **Production**: Requires `GOOGLE_CLIENT_*` and `FACEBOOK_CLIENT_*` in frontend/.env
- **Development**: Mock OAuth available (see signup.html lines 52-59)
- **Mock links**: `/auth/callback/google?mock=true` and `/auth/callback/facebook?mock=true`
- Mock users are created with `mock_{provider}_12345` as provider_id

### Friendship Bidirectionality
- Friendships require two database records:
  1. `Friendship(user_id=A, friend_id=B)`
  2. `Friendship(user_id=B, friend_id=A)`
- This allows querying "friends of user" in one direction only
- See backend/app.py:125-126 for implementation

### HTMX Response Format
- HTMX endpoints return **HTML snippets**, not JSON
- Example: `/api/share` returns HTML for new history items
- Example: `/api/history_partial` returns full history list as HTML
- Only backend `/api/users/*` endpoints return JSON

### Port Configuration
- Frontend: Port 5000 (default)
- Backend: Port 5001 (default)
- Frontend calls backend at `BACKEND_URL` from frontend/.env
- Changing ports requires updating both .env files

### Database Initialization
- Database tables are created automatically on backend startup
- See backend/app.py:64-65: `db.create_all()` runs within app context
- No migration system (Alembic) - tables recreated on each startup

## Testing

**Current state**: No test files exist.

**Planned** (per README):
- Backend tests: `test_app.py` using pytest
- Frontend tests: `test_app.py` for template rendering and HTMX interactions

**Test dependencies** (to be added):
- pytest
- pytest-flask

## Dependencies

### Backend (backend/pyproject.toml)
- `flask`: Web framework
- `sqlalchemy`: ORM
- `flask-sqlalchemy`: Flask-SQLAlchemy integration
- `python-dotenv`: Environment variable management

### Frontend (frontend/pyproject.toml)
- `flask`: Web framework
- `authlib`: OAuth client library
- `requests`: HTTP client for backend API calls
- `python-dotenv`: Environment variable management

### Development
- `uv`: Package manager and virtual environment manager
- Python >=3.10 (specified in .python-version)

## API Documentation

OpenAPI 3.0 spec is in `backend/openapi.yaml` but note:
- Some endpoints documented there are frontend routes, not backend API
- Actual backend API endpoints are in backend/app.py (lines 67-153)
- Frontend routes are in frontend/app.py

## Common Tasks

### Adding a new backend endpoint
1. Add route handler in backend/app.py
2. Document in backend/openapi.yaml
3. Call from frontend using `requests` or create new frontend route with HTMX

### Adding OAuth provider
1. Add provider config in frontend/app.py (lines 22-43 show pattern)
2. Add provider-specific token/userinfo handling in `auth_callback` (lines 91-140)
3. Add credentials to frontend/.env

### Changing database schema
1. Modify model class in backend/app.py
2. Tables will be recreated on backend restart (no migration system)
3. For production data: backup database first or implement migrations

### Customizing styling
- TailwindCSS via CDN (index.html:8, signup.html:8)
- Custom CSS in `<style>` tags in templates
- Reusable `.glass` class for consistent styling
