# 🩺 AarogyaAI — AI-Powered Personal Health & Wellness Assistant

A working starter implementation of the AarogyaAI project: a Flask + SQLite
backend, a rule-based AI engine (safety layer, wellness score, recommendation
engine, weekly report, optional LLM-backed chat), and a plain HTML/CSS/JS
frontend. No build step required for the frontend, and the backend runs
fully offline (the chatbot works with or without an LLM API key).

This is a wellness-support tool, **not** a diagnostic or medical device.
See `backend/ai_engine/safety_rules.py` for the deterministic emergency
escalation layer that runs ahead of any AI-generated response.

## Folder structure

```
AarogyaAI/
├── backend/
│   ├── app.py                  # Flask app factory + blueprint registration
│   ├── run.py                  # `python run.py` starts the server
│   ├── config.py                # env-driven configuration
│   ├── db.py                    # sqlite3 data-access layer
│   ├── seed_demo_data.py        # optional: creates a demo user + 7 days of logs
│   ├── utils/
│   │   └── auth_utils.py        # JWT helpers + @token_required decorator
│   ├── ai_engine/
│   │   ├── safety_rules.py      # red-flag / crisis keyword detection (deterministic)
│   │   ├── wellness_score.py    # 0-100 composite score + per-dimension breakdown
│   │   ├── recommendations.py   # rule-based, priority-ordered suggestions
│   │   ├── chat_engine.py       # safety check -> optional LLM -> rule-based fallback
│   │   └── weekly_report.py     # aggregates 7 days of daily_logs
│   └── routes/
│       ├── auth_routes.py       # POST /api/auth/signup, /login
│       ├── profile_routes.py    # GET/PUT /api/profile
│       ├── daily_log_routes.py  # POST/GET /api/logs/... (the daily activity store)
│       ├── chat_routes.py       # POST /api/chat, GET /api/chat/history
│       ├── dashboard_routes.py  # GET /api/dashboard
│       ├── reminder_routes.py   # CRUD /api/reminders
│       └── report_routes.py     # GET /api/reports/weekly
├── database/
│   ├── schema.sql               # full table definitions (see below)
│   └── aarogyaai.db             # created automatically on first run
├── frontend/
│   ├── index.html               # login / signup
│   ├── dashboard.html           # stats, score, logging forms, trend chart
│   ├── chat.html                # AI chat
│   ├── reminders.html           # reminders CRUD
│   ├── report.html              # weekly AI report
│   ├── css/style.css
│   └── js/ (api.js, auth.js, dashboard.js, chat.js, reminders.js)
├── requirements.txt
└── .env.example
```

## Running it

**1. Backend**

```bash
cd AarogyaAI
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example backend/.env    # edit if you want to plug in a real LLM
cd backend
python run.py                   # starts on http://localhost:5000
```

The SQLite database and all tables are created automatically on first run
(`db.init_db()` runs inside `create_app()`).

Optional — load a demo user with a week of sample data so the dashboard
isn't empty on first look:

```bash
python seed_demo_data.py
# log in with demo@aarogyaai.app / demo1234
```

**2. Frontend**

The frontend is static HTML/CSS/JS — no build step. Simplest option:

```bash
cd frontend
python -m http.server 8080
# open http://localhost:8080
```

`frontend/js/api.js` points at `http://localhost:5000/api` by default —
change `API_BASE` there if your backend runs elsewhere.

## How daily activity is stored (Section 21 of the project spec)

Every log — sleep, water, exercise, meals, mood/stress, symptoms — is
persisted to SQLite so the dashboard, wellness score, and weekly report are
all computed from real history rather than one-off inputs:

- **`daily_logs`** — one row per user per calendar day (sleep_hours,
  water_ml, exercise_minutes, stress_level, symptoms_text, wellness_score,
  score_breakdown as JSON).
- **`exercise_entries`** / **`meal_entries`** — one row per logged session /
  meal, so a single day can have several; their totals roll up into that
  day's `daily_logs` row.
- **`chat_history`** — every chat turn, flagged if it triggered the safety
  layer.
- **`reminders`** — user-created reminders.

`POST /api/logs/today` is called every time the user logs sleep, stress, or
symptoms; `POST /api/logs/exercise` and `POST /api/logs/meal` append entries
and update the running daily totals; each of these recomputes and stores
that day's wellness score (`backend/ai_engine/wellness_score.py`) so history
never goes stale.

## The AI pieces, and where to look

| Feature (from the project spec) | File |
|---|---|
| Conversational assistant | `ai_engine/chat_engine.py` |
| Red-flag / crisis detection (runs before any LLM call) | `ai_engine/safety_rules.py` |
| Personalized recommendations | `ai_engine/recommendations.py` |
| Wellness Score | `ai_engine/wellness_score.py` |
| Weekly AI report | `ai_engine/weekly_report.py` |

The chatbot works with **zero configuration** — if `LLM_API_KEY` is unset in
`backend/.env`, `chat_engine.py` automatically falls back to built-in
rule-based responses, so the whole app is demoable without internet access.
To use a real LLM, set `LLM_API_KEY` / `LLM_API_URL` / `LLM_MODEL` in
`backend/.env` for any OpenAI-compatible chat-completions endpoint.

## Next steps / good hackathon add-ons

- Swap the keyword-based nutrition rating for a small food-database lookup
  (Section 9 mentions an Indian-food-focused database).
- Add push/browser notifications for `reminders` instead of a static list.
- Add a `/api/reports/weekly` PDF export for judges.
- Multilingual chat (English + Telugu + Hindi) by translating the system
  prompt and rule-based fallback strings.
