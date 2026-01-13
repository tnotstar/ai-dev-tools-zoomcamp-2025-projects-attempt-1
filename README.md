# PoshBullet - Collaborative URL Sharing Platform

## Problem Description

PoshBullet is a minimalistic, secure, and collaborative URL sharing platform designed to streamline the sharing of links between friends and colleagues. In a world of fragmented communication channels, PoshBullet offers a unified space where users can invite friends, share URLs instantly, and maintain a persistent history of shared links.

The platform solves the problem of "lost links" in chat streams by creating a dedicated, searchable history of shared content, emphasizing ease of use through a modern, glassmorphic interface and seamless, real-time interactions.

## AI System Development

This project was built using an advanced AI-assisted workflow, leveraging **Antigravity** (an agentic coding assistant).

*   **Tools & Workflow**: The development followed an iterative prompt-driven approach. The AI acted as a Senior Full Stack Architect, implementing features based on high-level functional requirements.

*   **MCP (Model Context Protocol)**: The system utilizes MCP to manage context and tool execution, allowing the AI to interact with the file system (`write_to_file`, `list_dir`), run terminal commands (`uv run`), and perform codebase searches (`grep_search`), enabling a fully autonomous development cycle.

*   **Agentic Capabilities**: The AI managed the refactoring of a monolithic prototype into a decoupled microservices architecture (Frontend/Backend split), handled database migrations (sqlite3 to SQLAlchemy), and implemented complex UI logic (HTMX interactions).

## Technologies and System Architecture

The system follows a decoupled architecture separating the presentation layer from the data/logic layer:

### Architecture

*   **Frontend Service (Port 5000)**: A Flask application that handles:
    *   User Authentication (OAuth via Authlib).
    *   Session Management (Server-side cookies).
    *   UI Rendering (Jinja2 templates + TailwindCSS).
    *   Gateway Logic (Proxies API requests to the Backend).

*   **Backend Service (Port 5001)**: A stateless Flask API that handles:
    *   Data Persistence (SQLAlchemy ORM).
    *   Business Logic (Friendships, Sharing).
    *   JSON API Responses.

### Tech Stack
*   **Frontend**: HTML5, TailwindCSS (Styling), HTMX (Dynamic interactions), Flask (Server).
*   **Backend**: Python, Flask, SQLAlchemy.
*   **Database**: SQLite (In-Memory for MVP, file-based supported).
*   **Package Management**: `uv` (Ultra-fast Python package installer).

## Front-end Implementation

The frontend is built for responsiveness and visual appeal using a "Glassmorphism" aesthetic.

*   **Structure**:
    *   `templates/index.html`: Main dashboard with dynamic "Hero" vs "Dashboard" views.
    *   `templates/signup.html`: Dedicated login/signup page with Mock OAuth support.

*   **Interactions**: Uses **HTMX** for smooth partial page updates (e.g., submitting a URL updates the history list without a full reload).

*   **Testing**: (Planned) Tests for rendering and interactions are scoped for `test_app.py`.

## API Contract (OpenAPI)

The backend adheres to the OpenAPI 3.0 specification defined in `backend/openapi.yaml`. This document serves as the contract for:
*   `GET /health`
*   `POST /api/users/auth`
*   `POST /api/shares`
*   `GET /api/users/{id}/history`

## Back-end Implementation

The backend is a robust REST API:

*   **ORM**: Uses **SQLAlchemy** for database abstraction.
*   **Models**: `User`, `Friendship` (bi-directional), `SharedUrl`.
*   **Configuration**: uses `python-dotenv` to load `backend/.env`.

## Database Integration

*   **Technology**: SQLite.
*   **Configuration**: Controlled via `DATABASE_URL`.
    *   Default: `sqlite:///:memory:` (Non-persistent, resets on restart).
    *   Persistent: `sqlite:///database.db` (Supported by changing `.env`).

## Setup and Reproducibility

The project is designed for instant setup using `uv`.

### Prerequisites

*   Python 3.10+
*   `uv` installed (`pip install uv`)

### Quick Start (One-Line)

Run the entire environment (Frontend + Backend) with a single command:

```bash
uv run python main.py
```

This script will:
1.  Install/Sync dependencies for both backend and frontend.
2.  Start the Backend on port 5001.
3.  Start the Frontend on port 5000.
4.  Open `http://localhost:5000`.

## Containerization (Planned)

Support for Docker is planned. The architecture is ready for containerization:
*   `backend/Dockerfile` -> Exposes port 5001.
*   `frontend/Dockerfile` -> Exposes port 5000.
*   `docker-compose.yaml` -> Orchestrates both services.

## Integration Testing (Planned)

Integration tests will cover:
1.  User flow: Signup -> Invite Friend -> Share URL.
2.  Database constraint checks (unique providers).
3.  Cross-service communication (Frontend -> Backend).

## Deployment

The application is ready for cloud deployment (e.g., Google Cloud Run).
*   **Requirements**: Two services (Frontend, Backend).
*   **Environment**: Set `BACKEND_URL` in frontend service to point to the backend service URL.

## CI/CD Pipeline (Planned)

A GitHub Actions workflow is planned to:
1.  Lint code with `ruff`.
2.  Run `pytest` suites.
3.  Build and Push Docker images upon success.

---

## Used prompts

### Initial prompt

> ### Context & Persona
>
> Act as a Senior Full Stack Software Architect. We are building an MVP for an "Online URL Sharing Platform". The goal is to create a collaborative environment where an interviewer can share a link with a partner from his friend-list, and have a history of the shared links.
>
> ### Technical Stack:
>
> * **Frontend:** HTMX and TailwindCSS for styling.
> * **Backend:** Python and Flask.
> * **API Documentation:** OpenAPI 3.0 (Swagger).
>
> ### Functional Requirements
>
> * **Sharing URLs Database:** For this MVP project, we will use a SQLite3 database at backend-side.
>
> * **Session Management:** The system must support Google and Facebook authentication, and it must keep a list of sign-up users.
>
>   Then estándar Flask session manager must implemented to protect user's friend-list and shared urls.
>
> * **Friend Invitation**: User A invitates User B throught a invite link.  If User B was already signed up, User B is added to User A friend-list and vice-versa.  If not, User B must sign-up before accept invitation.
>
> * **URL Sharring**: User A has a single form to select one o more users from its friend-list, and a text box field to input the url to be shared.
>
> ### Deliverables (Response Format)
>
> Please provide the complete implementation in a single response following this structure:
>
> #### Project Structure: A file tree overview
>
> 1. Project root (`/workspaces/ai-dev-tools-zoomcamp-2025-projects-attempt-1`):
>    * **Backend Implementation (`backend`)**
>      - server.py: Flask setup, and API implementation.
>      - openapi.yaml: The OpenAPI 3.0 specification document describing the HTTP endpoints (e.g., health check, user sign-up, sign-in, invites, send links, and so on).
>
>    * **Frontend Implementation (`frontend`)**
>      - index.html: When the user was signed-in: a combo box with the user's friends, and a chat-like history of shared URLs to. Wehn the user was not signed-in: two buttons for "Sign-In" and "Sign-Up".
>      - signup.html: A single form to select sign-up with Google or Facebook.
>      - invite.html: A page we the generated invitation link.
>
> ### Setup Instructions
>
> * uv install commands to get this running locally.
>
> ## Important Constraint
>
> Ensure all code provided is functional, imports are correct, and the database logic handles the backend i/o operations.

## 
> Please use "/workspaces/ai-dev-tools-zoomcamp-2025-projects-attempt-1" as the project root, and move all asset inside "url-sharing-platform" folder, to the new root. Finally, remove "url-sharing-platform" when it was empty.

> Install "uv" if it is not available in the environment.

> Please, rename the project from "LinkShare" to "PoshBullet".

> Now convert the project to an "uv" workspace, and two subprojects "backend" and "frontend".  Each one with its own "pyproject.toml" files.

> We need to separate the project between the "backend" side and "frontend" side.  Refactor the workspace to implement thoses side as two independant Flask applications. Use each "pyproject.toml" file to manage dependencies. Authentication logic must be moved to the "frontend" and the "backend" must server frontend's requests in a local network.

> Modify the "backend" code to use "SQL Alchemy" as a ORM. Then modify the configuration to use "dotenv" in both "backend" and "frontend" and finally, move hostnames, ports and database configuration to two ".env" file for each side. To made project non-persistent user an in memory sqlite database by default.

## Integrating both servers to deployment at Google CloudRun

> Task: Enable running both the Flask backend and the HTMX-based frontend concurrently for > the URL Sharing Platform.
>
> Technical Requirements:
>
>    Process Management: Provide a method to start the server and any necessary assets using a single command (e.g., using a Makefile, a Python runner script, or honcho/foreman).
>
>    Development Server: Configure the Flask app to run in DEBUG mode with hot-reloading enabled.
>
>    CORS & Proxy: Ensure the frontend (HTMX) can communicate with the backend without Cross-Origin issues. Since we are using Jinja2 templates served by Flask, explain how the routing handles both the UI and the API endpoints.
>
>    Task Automation: Create a dev.py script or a Taskfile that:
>
>        Checks if the SQLite database exists (and creates it if not).
>
>        Installs dependencies via uv.
>
>        Starts the Flask server on localhost:5000.
>
>Deliverable:
>
>    The Python code for the runner script.
>
>    The updated pyproject.toml including a custom script command if applicable.
>
>    Clear instructions on how to launch the entire environment with one line.

## Prompt for test cases

> Context: Continuing with the "Online Coding Interview Platform" project we just implemented. I now need to ensure the reliability of the application by adding automated tests for both the frontend and backend.
>
> Task: Act as a Lead QA Automation Engineer. Please generate the test files and update the documentation following these requirements:
>
> 1. Backend Testing (Node/Express):
>
> Stack: Use pytest.
> Scope: Create a test file `test_app.py`.
>
> Test Cases:
>
> GET /health: Verify the server returns a 200 OK status.
> POST /user: Verify it returns a unique room ID and a 201 Created status.
>
> 2. Frontend Testing (HTMX):
>
> Scope: Create a test file `test_app.py`.
>
> Test Cases:
>
> Rendering: Verify that the "Invite Friend" or "Send URL" buttons render correctly on the landing page.
> Editor Component: Verify that the code editor container loads (mocking the heavy monaco-editor if necessary to prevent test crashes).
>
> 3. Documentation Update (README.md):
>
> Provide an updated "Testing" section for the README.md.
>
> Include the specific commands to install the testing dependencies (npm install -D ...) and the commands to run the tests (npm test).
>
> Deliverables:
>
> The code for backend/server.test.js (or equivalent path).
>
> The code for frontend/src/App.test.jsx.
>
> The modified package.json scripts needed to run these tests.
>
> The updated text snippet for the README.md.