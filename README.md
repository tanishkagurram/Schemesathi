# SchemeSathi 🇮🇳

A single-file Flask web app that helps Indian citizens discover government
welfare schemes (scholarships, pensions, loans, health cover, etc.) they're
eligible for — by profile filters, free-text search, or an AI chat advisor.

## What it is

This is a **Python/Flask port of a React application** — the entire app
(routes, in-memory data, HTML templates, and inline CSS/JS) lives in one
file, `schemesathi.py`. There's no separate frontend build, database, or
static-file pipeline; Flask renders full HTML pages per request using
`render_template_string`.

## Features

- **Login / Signup** — a simple demo auth flow (`/login`, `/signup`,
  `/logout`) backed by Flask's server-side `session`, not a real user
  database. The login page explicitly says *"Demo: use any email +
  password to sign in"* — any non-empty email/password logs you in.
- **Home dashboard** (`/`) — a personalized welcome, quick stats
  (1500+ schemes, 28 states, 10Cr+ beneficiaries — static display copy),
  a search bar, and a "Saved Schemes" strip pulled from the session.
- **Search** (`/search`) — free-text search across scheme name, benefit,
  category, and tag, plus tag-based filter chips (Education, Skills,
  Pension, Loan, Health, Farming, etc.).
- **Schemes** (`/schemes`) — the full scheme catalog with a profile-based
  filter form (age, income, gender, occupation) that narrows results using
  each scheme's eligibility rules; falls back to a small default list if
  nothing matches.
- **Save/unsave schemes** (`/save/<id>`) — toggles a scheme in/out of the
  session's saved list.
- **AI Chat advisor** (`/chat`, `/api/chat`) — a chat UI where users
  describe themselves in plain language (or Hinglish) and get scheme
  recommendations back from an LLM, with quick-prompt suggestion chips.
- **Settings** (`/settings`) — edit profile fields (name, email, phone,
  state, occupation, age, income) and preferences (notifications, dark
  mode, UI language), all persisted in the session.
- **Multi-language UI** — a `TRANSLATIONS` dictionary covers English,
  Hindi, Kannada, Tamil, Telugu, and Marathi; every label rendered through
  the page templates is looked up from the user's selected language.

## How eligibility filtering works

`filter_schemes()` matches a scheme against a user's inputs on six axes:

- free-text query (name / benefit / tag / category)
- selected tag (or "All")
- age within the scheme's `minAge`–`maxAge` range
- income at or below the scheme's `maxIncome` cap
- gender (`all` or an exact match)
- state (`"all"` in the scheme's state list, or an exact match)
- occupation, loosely mapped to each scheme's `category` (Student, Farmer,
  Entrepreneur/Self-employed, or General schemes that everyone qualifies
  for)

The scheme catalog (`SCHEMES`) is a small hardcoded list of 10 real,
well-known Indian government schemes (PM Scholarship, Skill India, PM
Kisan, Ayushman Bharat, Mudra Loan, Startup India Seed Fund, etc.), each
with its benefit text, required documents, and an official application
link.

## How the AI chat works

`/api/chat` is a JSON endpoint called by the chat page's JavaScript. On
each message it:

1. Appends the user's message to the session's chat history.
2. Builds a system prompt listing every scheme name/benefit/tag so the
   model can recommend from the actual catalog.
3. Sends the conversation to **Anthropic's Messages API**
   (`https://api.anthropic.com/v1/messages`, model
   `claude-sonnet-4-20250514`) using Python's built-in `urllib.request` —
   no third-party HTTP or SDK dependency.
4. Returns the assistant's reply as JSON, and keeps the last 30 messages
   in the session.

> ⚠️ **As written, the request to the Anthropic API has no
> `x-api-key`/`anthropic-version` headers or key configured anywhere in
> the file.** As-is, this call will fail — you'll need to add your own
> Anthropic API key (e.g. read from an environment variable) and the
> required headers before `/api/chat` will work. See "Known limitations"
> below.

## Tech stack

- **Flask** (routing, sessions, Jinja2 `render_template_string`)
- **Python standard library** (`urllib.request`, `json`) for the outbound
  Anthropic API call — no `requests` or Anthropic SDK dependency
- All UI is hand-written HTML/CSS/vanilla JS embedded as Python strings —
  no frontend framework, build step, or static assets folder

## How to run it

Requires Python 3 with Flask installed.

```sh
pip install flask
python schemesathi.py
```

Then open **http://localhost:5000** in your browser. You'll land on the
login page — enter any email and any password (6+ characters not
required for login, only for signup) to get in.

The app runs with `debug=True` on port 5000 by default (see the bottom of
`schemesathi.py`).

## Project structure

Everything lives in **one file**, organized top-to-bottom as:

```
schemesathi.py
├── SCHEMES, STATE_LIST, OCCUPATION_OPTIONS, TAG_LIST   Static scheme/catalog data
├── TRANSLATIONS                                        UI strings per language
├── get_initials(), filter_schemes()                    Helper functions
├── BASE_HTML / AUTH_HTML (implied)                     Raw HTML/CSS template strings
├── shell()                                              Shared page chrome (nav, sidebar)
├── render_scheme_cards()                                Scheme card HTML builder
├── /login, /signup, /logout                             Auth routes (session-based)
├── /save/<id>                                           Save/unsave a scheme
├── /            (home)                                  Dashboard
├── /search                                              Free-text + tag search
├── /schemes                                             Full catalog + profile filter
├── /chat, /api/chat                                     AI chat page + backend call
├── /settings                                            Profile & preference editing
└── if __name__ == "__main__": app.run(...)               Entry point
```

## Known limitations

- **Not production-ready auth.** Login accepts any email/password combo
  and there's no password hashing, database, or account persistence —
  everything lives in the Flask session and resets when the session
  expires or the server restarts.
- **`app.secret_key` is hardcoded** in the source
  (`"schemesathi-secret-2024"`) — this must be replaced with a securely
  generated, environment-provided secret before any real deployment,
  since anyone with this key can forge session cookies.
- **The Anthropic API call is missing authentication.** No API key is
  read or sent with the request in `/api/chat`, so the AI chat feature
  will fail until you wire in `ANTHROPIC_API_KEY` (e.g. via
  `os.environ`) and add the required `x-api-key` / `anthropic-version`
  headers.
- **In-memory/session-only data.** Saved schemes, profile edits, and chat
  history are stored in the browser's session cookie server-side state,
  not a database — nothing persists across different browsers/devices for
  the same "account."
- **Small, static scheme catalog.** Only 10 example schemes are included;
  this is a demo dataset, not a live feed from data.gov.in or similar.
- **`debug=True` in the entry point** should be turned off before any
  real deployment, since Flask's debugger can expose a remote code
  execution risk if left on in production.
