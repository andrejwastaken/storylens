# StoryLens

Paste a news article URL and get an evidence-backed **Story Profile**: a deterministic 0-100
Trust Score, source reputation, corroboration across independent outlets, evidence quality per
claim, headline/body consistency, sensationalism, political framing, and how different outlets
cover the same story.

StoryLens is **not** a fake-news detector. It never claims a story is definitively true or false -
it surfaces signals (source reputation, corroboration, evidence per claim) and lets you judge for
yourself. The final Trust Score is always computed by plain, deterministic Python code
(`backend/app/scoring.py`) - the LLM only ever produces sub-signals that feed into it.

## Architecture

```
React + Tailwind (frontend/)
        |  HTTP (POST /analyze)
        v
FastAPI backend (backend/)
        |
        +--> Firecrawl   - article extraction (original + related sources)
        +--> OpenAI       - claim extraction, language/bias analysis, evidence comparison
        +--> Exa          - independent/corroborating source search
        +--> PostgreSQL   - persistence (sources, articles, stories, claims, evidence, analyses)
        +--> scoring.py   - deterministic Trust Score engine (plain Python, not the LLM)
```

## 1. Prerequisites

- Python 3.13 (`brew install python@3.13`)
- Node.js 20+ (already installed if you can run `node -v`)
- PostgreSQL (`brew install postgresql@17`)

## 2. Get your API keys

You need three keys. All have generous free tiers - none require a credit card to start.

| Service | What it's for | Where to get it | Free tier |
|---|---|---|---|
| **OpenAI** | Claim extraction, language/bias analysis, evidence comparison (structured JSON output) | https://platform.openai.com/api-keys - sign up, add a bit of billing credit, click "Create new secret key" | Pay-as-you-go, no free tier, but cheap per request (GPT-5.6 Sol: ~$5/$30 per 1M tokens) |
| **Firecrawl** | Turns article URLs into clean markdown + metadata | https://www.firecrawl.dev/app - sign up, copy your key from the dashboard | 1,000 free credits/month, no card required. Works without a key too ("Keyless" tier) but rate-limited - fine for quick testing, get a key before a live demo. |
| **Exa** | Searches the web for independent coverage of a story/claim | https://dashboard.exa.ai/api-keys - sign up (Google or email), copy your key | New accounts get $20 free credit, plus $10/month on the free tier, no card required |

Put them in `backend/.env` (see step 4). **Never commit `.env` files** - `.gitignore` already
excludes them.

## 3. Database setup

```bash
brew services start postgresql@17
createdb storylens
```

## 4. Backend setup

```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# now edit backend/.env and paste in your OPENAI_API_KEY, FIRECRAWL_API_KEY, EXA_API_KEY
```

Run it:

```bash
uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on startup (`Base.metadata.create_all` - no migrations for the
MVP). Visit http://localhost:8000/docs for interactive API docs.

## 5. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # defaults to VITE_API_URL=http://localhost:8000, adjust if needed
npm run dev
```

Visit http://localhost:5173.

## 6. Use it

Paste a real article URL (Reuters, AP, BBC, a smaller outlet, etc.) and click **Analyze**. The
first request takes ~20-60 seconds because the backend extracts the article, calls the LLM twice,
searches Exa, and scrapes up to 5 related articles with Firecrawl.

You can drag the "Adjust weights" sliders on the Story Profile to see the Trust Score recompute
live (the frontend mirrors the exact same weighted-sum formula as the backend engine).

## Repository structure

```
backend/
  app/
    main.py                     FastAPI app + CORS + startup table creation
    config.py                   Settings loaded from .env
    database.py                 SQLAlchemy engine/session
    models.py                   ORM models: sources, articles, stories, claims, evidence,
                                 analyses, story_articles
    schemas.py                  API request/response Pydantic models
    scoring.py                  Deterministic Trust Score engine (plain Python)
    seed_sources.py             Small curated outlet reputation table (signal, not fact)
    crud.py                     Small persistence helpers
    routers/analyze.py          POST /analyze orchestration endpoint
    services/
      firecrawl_client.py       Article extraction
      exa_client.py              Independent-coverage search
      llm/
        base.py                  Abstract LLMProvider interface (swap providers later)
        openai_provider.py       OpenAI implementation (Structured Outputs)
        schemas.py               Pydantic schemas for LLM structured output
        prompts.py               Prompt text for both LLM passes
  requirements.txt
  .env.example

frontend/
  src/
    App.tsx                     Top-level page: input -> loading -> Story Profile
    api.ts                      POST /analyze client
    scoring.ts                  Client-side mirror of the weighted-sum formula (for live sliders)
    types.ts                    TypeScript types matching backend schemas.py
    components/
      UrlInputForm.tsx
      LoadingSteps.tsx
      TrustScoreGauge.tsx
      SubscoreBars.tsx           Includes the adjustable weight sliders
      ArticleHeader.tsx          Title/source/author/date + political framing signal
      ReasonsWarnings.tsx
      ClaimsList.tsx
      OutletFraming.tsx
      RelatedSources.tsx
      StoryProfile.tsx           Composes all of the above
  .env.example
```

## How the Trust Score is computed

`backend/app/scoring.py` combines five 0-100 sub-scores with configurable weights (defaults: 25%
source reliability, 30% corroboration, 25% evidence quality, 10% headline/body consistency, 10%
anti-sensationalism):

- **Source reliability** - looked up from a small curated table of ~40 well-known outlets
  (`seed_sources.py`). Unknown domains get a neutral default (50). This is a directional signal,
  not a fact about the outlet.
- **Corroboration** - counts *independent* outlets covering the story. Related articles are
  clustered by domain and by near-duplicate text (via `difflib`) so that multiple sites copying
  the same wire story don't count as independent corroboration.
- **Evidence quality** - importance- and confidence-weighted average of per-claim verdicts
  (supported / partially_supported / unverified / contradicted), further weighted by the
  reliability of the citing sources (a claim "supported" by Reuters counts more than one
  "supported" by an unknown blog).
- **Headline/body consistency** and **sensationalism** - signals produced by the LLM in pass 1,
  passed through as-is (they are sub-signals, not the final score).

The LLM never outputs a final Trust Score - only these sub-signals feed a plain-Python weighted
average.

## What's out of scope for this MVP (by design)

No Docker, no database migrations tool, no user accounts, no browser extension, no
from-scratch ML model, no comprehensive global source-rating database, no sophisticated
AI-image detection, no claim of definitively "fake" vs "real". See the P2 backlog (ElevenLabs
audio summary, fal.ai AI-image signal, caching, richer source history) for possible follow-ups
after the core demo works.

## Deployment (after the demo works locally)

- **Frontend**: Netlify - point it at `frontend/`, build command `npm run build`, publish
  directory `dist`, set `VITE_API_URL` to your deployed backend URL.
- **Backend**: Render - a Python web service, build command `pip install -r requirements.txt`,
  start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, plus a managed PostgreSQL
  instance (Render Postgres or any managed provider) wired up via `DATABASE_URL`.
