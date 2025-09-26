# Personal Assistant Chatbot — Complete Guide

This document explains what this project is, how it works, how to run it in development and production, and what technologies it uses.

## Summary

Personal-Assistance-Chatbot is a Django 5 web app that provides a simple personal assistant with:

- Chat UI to interact with the assistant
- Tasks, Notes, Reminders, and Events management
- Optional ML-based intent routing (scikit-learn)
- Periodic background job (Celery + Redis) to process due reminders

Out of the box it uses SQLite for development; you can switch to PostgreSQL with a single environment variable.

## Tech Stack

- Language: Python 3.10+
- Web framework: Django 5.x
- Task queue: Celery 5.x
- Broker/result backend: Redis 5.x+
- ORM/Database: SQLite (default), PostgreSQL (optional)
- ML (optional): scikit-learn (TF‑IDF + Logistic Regression)
- Config: python-dotenv for `.env` files

Key Python packages (see `requirements.txt`):

- `Django` (web framework)
- `python-dotenv` (load env vars from `.env`)
- `psycopg2-binary` (PostgreSQL driver; optional)
- `celery`, `redis` (task queue + backend)
- `scikit-learn` (optional ML intent router)

No external third‑party HTTP APIs are called by the app; everything runs locally.

## Project Structure

- `manage.py` — Django entry point
- `personal_assistant/` — project package (settings, URLs, WSGI/ASGI, Celery app)
- `chat/` — chat UI, assistant orchestration, ML router, message log
- `tasks/`, `notes/`, `reminders/`, `events/` — feature apps with models, views, templates
- `templates/` (optional) — extra template dir if you create it
- `.env.example` — example environment configuration

Notable files:

- `personal_assistant/settings/base.py` — core settings (DB, Celery, installed apps)
- `personal_assistant/settings/dev.py` — development overrides (`DEBUG=True`)
- `personal_assistant/settings/prod.py` — production hardening (HTTPS flags)
- `personal_assistant/celery.py` — Celery app config; auto-discovers tasks
- `personal_assistant/urls.py` — URL routing (chat home, tasks, notes, reminders, events)
- `chat/services.py` — Assistant, intent dispatch, natural date parser
- `chat/ml.py` — optional TF‑IDF + Logistic Regression intent router

## Features & Flows

### Chat

- Route: `/`
- Renders last 50 `Message` entries and a form input
- On submit, saves a user message, calls the `Assistant`, saves its reply

### Assistant & Intents

- First use trains or primes the router (using seed phrases and any saved `TrainingPhrase` records)
- Predicts one of: `tasks`, `notes`, `reminders`, `events`, `time`, `smalltalk`
- If confidence is low or ML unavailable, falls back to rules via keywords

Supported commands (examples):

- Tasks: `add task Buy milk tomorrow at 09:00`
- Notes: `note Trip: Pack passport and charger`, `search notes passport`
- Reminders: `remind me in 10 minutes to stretch`, `remind me tomorrow at 9 to call mom`
- Events: `add event 2025-08-25 14:00 - Demo @HQ`
- Time: `what time is it`, `date`

### Apps

- Tasks — list, add, mark complete (`/tasks/`)
- Notes — list, add, full-text search (`/notes/`)
- Reminders — list, add, cancel (`/reminders/`)
- Events — list, add (`/events/`)

### Profile, Projects, and Persona (New)

- About page: `/about/` shows your profile, projects, and FAQs.
- Manage from Admin:
  - Profile: display name, bios, links
  - Project: title, summary, link, active flag, order
  - QAPair: frequently asked questions
  - Persona: tone, greeting/closing templates, how to refer to you
- Chat intents:
  - “about me”, “who am i”, “profile” → profile response
  - “my projects”, “projects” → projects list response
  - Persona styling wraps replies with greeting/closing if set

### Natural Date Parsing

- Understands phrases like: `in 10 minutes`, `today at 18:00`, `tomorrow at 9`, `on 2025-08-25 14:00`
- Timezone from `TIME_ZONE` setting (`Europe/Paris` by default)

### Background Jobs (Celery)

- Periodic task `reminders.tasks.check_due_reminders` runs every 30 seconds
- Marks reminders due at or before now as delivered (placeholder for real notifications)
- Requires Redis if you want this automation active

## Setup (Development)

Windows PowerShell examples below; adapt for macOS/Linux.

1) Create and activate a virtualenv

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Create your `.env`

```powershell
Copy-Item .env.example .env
# Edit as needed (SECRET_KEY, TIME_ZONE, DATABASE_URL, Redis URLs)
```

4) Initialize the database

```powershell
python manage.py makemigrations
python manage.py migrate
```

5) Create a superuser (optional, for Django admin)

```powershell
python manage.py createsuperuser
```

6) Run the dev server

```powershell
python manage.py runserver 0.0.0.0:8000
```

Open http://127.0.0.1:8000/ in your browser.

Seed your profile and projects via Admin:

- `python manage.py createsuperuser`
- Go to `/admin/` → Profile app → add a Profile, a few Projects, and optionally a Persona and Q&A entries

## Celery & Redis (Reminders Automation)

Start Redis (choose one):

- Docker: `docker run --rm -p 6379:6379 redis:7-alpine`
- Native install: ensure Redis runs on `localhost:6379`

Run Celery (Windows requires `--pool=solo`):

```powershell
celery -A personal_assistant worker -l info --pool=solo
celery -A personal_assistant beat -l info
```

The beat scheduler triggers `check_due_reminders` every 30 seconds.

## PostgreSQL (Optional)

Switch from SQLite to Postgres by setting `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
```

Docker example for local Postgres:

```powershell
docker run --name pa-postgres -e POSTGRES_USER=ai -e POSTGRES_PASSWORD=ai -e POSTGRES_DB=ai_assistant -p 5432:5432 -d postgres:16-alpine
```

Then run migrations against Postgres:

```powershell
python manage.py migrate
```

## Administration

- Admin at `/admin/`
- Models registered: Tasks, Notes, Reminders, Events, Chat Messages, Training Phrases
- Add `TrainingPhrase` (label, text) to improve or steer intent routing
 - ProfileApp models: Profile, Project, QAPair, Persona

### Retraining Without Restart

- Staff-only endpoint: `POST /retrain/` retrains the intent router and returns a JSON status
  - Example (PowerShell): `Invoke-WebRequest -Method POST http://127.0.0.1:8000/retrain/ -UseBasicParsing -SessionVariable s`
  - Or use browser devtools/fetch while logged in as staff

## Deployment Notes

- Use `personal_assistant.settings.prod` with `DJANGO_SETTINGS_MODULE=personal_assistant.settings.prod`
- Set `SECRET_KEY` to a strong value; set `ALLOWED_HOSTS` appropriately; set `DEBUG=0`
- Ensure HTTPS and security flags (HSTS, secure cookies) in `prod.py`
- Run a proper WSGI/ASGI server (e.g., gunicorn/uvicorn) behind a reverse proxy
- Set up Redis and run Celery worker + beat in the background
- Database: Provision Postgres and set `DATABASE_URL`

## Troubleshooting

- Error: `Requested setting DEBUG/DATABASES, but settings are not configured` when using `py -m django ...`
  - Use `python manage.py ...` (recommended) or set `$env:DJANGO_SETTINGS_MODULE = 'personal_assistant.settings.dev'`

- Error: `no such table: chat_message` or similar
  - Run `python manage.py makemigrations` and `python manage.py migrate`

- ML intent router does nothing / scikit-learn not installed
  - The app falls back to keyword rules; install `scikit-learn` to enable ML

- Celery tasks not running
  - Ensure Redis is running; start both Celery worker and beat processes; on Windows, add `--pool=solo`

- ML doesn’t recognize “about me/projects”
  - Ensure scikit-learn is installed and you have at least 2 labels overall; add more `TrainingPhrase` entries with label `profile` and `projects`, or rely on the built-in keyword fallback.

## creating superr user
$env:DJANGO_SUPERUSER_USERNAME='admin'
$env:DJANGO_SUPERUSER_EMAIL='admin@example.com'
$env:DJANGO_SUPERUSER_PASSWORD='StrongPassword123!'
python manage.py createsuperuser 

What You Can Do

Chat Messages (chat.Message)
Inspect the conversation log; add/delete messages if needed.
Fields: sender (user/assistant), text, created_at.
Training Phrases (chat.TrainingPhrase)
Teach the ML router new examples.
Label suggestions: tasks, notes, reminders, events, time, smalltalk.
Add phrases like: label reminders, text “nudge me in 10 minutes”.
Note: The assistant trains when it’s first created. After adding phrases, restart the dev server so the new data is used.
Tasks (tasks.Task)
Create tasks with optional due_at, mark complete from list view.
Filters: by is_completed; Search by title.
Appears on /tasks/.
Notes (notes.Note)
Create notes; Search by title and content in admin.
Appears on /notes/ and in chat “search notes …”.
Reminders (reminders.Reminder)
Create/cancel reminders; filter by delivered.
Celery marks due reminders as delivered; you can also toggle manually to simulate delivery.
Appears on /reminders/.
Events (events.Event)
Create events with starts_at, optional ends_at, location, details.
Search by title/location. Appears on /events/.
Typical Browser Workflow

Log in at /admin/.
Add a few Training Phrases to steer ML.
Open / to use the chat; add tasks/notes/reminders/events via natural language.
Use /tasks/, /notes/, /reminders/, /events/ to view/edit via forms.
Return to /admin/ anytime to review or correct data.
## License

Internal or project-specific; no explicit license file included.

Migrate & Run

Apply schema changes:
python manage.py makemigrations
python manage.py migrate
Start server: python manage.py runserver
Optional: create admin: python manage.py createsuperuser
Set Up Your Assistant Persona

Go to /admin/:
Profile: add display name, short/full bio, website, email, location.
Project: add active projects (title, summary, URL, order).
Persona (optional): set tone and templates:
Greeting template example: Hi, I’m {name}’s assistant — how can I help?
Closing template example: Happy to help!
Refer to you as: your first name (e.g., Alex).
QAPair (optional): add 2–5 FAQs you want answered.
Train the Intent Router

Add Training Phrases in Admin → Chat → Training phrases:
Labels to use: tasks, notes, reminders, events, time, smalltalk, profile, projects.
Add several examples per label (3–5+ each). Examples:
profile: “who am i”, “tell me about me”
projects: “my projects”, “what projects am i working on”
Retrain (no restart needed):
While logged in as staff: POST http://127.0.0.1:8000/retrain/
If scikit-learn isn’t installed or data is too small, it falls back to keyword routing.
How To Use In Chat

Persona/knowledge:
“about me”, “who am i”, “tell them about me” → response uses Profile, Persona, and first FAQ.
“my projects”, “what projects am i doing” → lists active projects with links.
Productivity:
“add task Buy milk tomorrow at 09:00”
“note Trip: Pack passport”, “search notes passport”
“remind me in 10 minutes to stretch”
“add event 2025-08-25 14:00 - Demo @HQ”
“what time is it”
Advanced Tips

Improve tone: add more smalltalk, profile, and projects training phrases to model your style.
Keep answers current: update Profile/Projects/FAQs in admin; retrain via /retrain/.
Share a public “About” page at /about/ for quick reference.z

Admin “Retrain intents” action

Location: Chat → Training phrases list in /admin/.
Select any rows (or none) → Actions → “Retrain intents (TF‑IDF + Logistic Regression)” → Go.
This retrains the same in‑memory assistant used by the chat view, so it takes effect immediately.
Training status endpoint

URL: GET /status/ (staff only).
Returns JSON like:
enabled: whether ML is available
trained: whether a pipeline is loaded
labels: list of labels the model knows
threshold: current confidence threshold
Seed in admin:
Go to /admin/ → Chat → Smalltalk pairs → Add
Example 1:
pattern: hi
is_regex: off
answers:
Hello!
Hi there!
Hey — how can I help?
Example 2:
pattern: how are you
is_regex: off
answers:
I’m doing great — ready to help!
All good here. How can I assist?
Try in chat:
“hi”, “hello”, “yo”, “how are you”, “thanks” → random friendly replies.
Add more pairs for varied conversation; use regex if you want flexible matching.