# StoryLens

Paste a news article URL and get an evidence-backed **Story Profile**: a deterministic 0-100 Trust Score, source reputation, corroboration across independent outlets, evidence quality per claim, headline/body consistency, sensationalism, political framing, and how different outlets cover the same story.

StoryLens is **not** a fake-news detector. It never claims a story is definitively true or false — it surfaces signals (source reputation, corroboration, evidence per claim) and lets you judge for yourself. The final Trust Score is always computed by plain, deterministic Python code (`backend/app/scoring.py`) — an LLM only ever produces sub-signals that feed into it.

---

## Architecture

```
React + Tailwind (frontend/)
        |  HTTP (POST /analyze)
        v
FastAPI backend (backend/)
        |
        +--> Firecrawl   - article extraction (original + related sources)
        +--> OpenAI      - claim extraction, language/bias analysis, evidence comparison
        +--> Exa         - independent/corroborating source search
        +--> PostgreSQL  - persistence (sources, articles, stories, claims, evidence, analyses)
        +--> scoring.py  - deterministic Trust Score engine (plain Python, not the LLM)
```

See [`docs/architecture.md`](docs/architecture.md), [`docs/database-schema.md`](docs/database-schema.md), and [`docs/flow.md`](docs/flow.md) for detailed diagrams of the system, the Postgres schema, and the full `/analyze` request flow. Presenting this project? See [`docs/PITCH.md`](docs/PITCH.md) for a 2-minute pitch script, demo steps, and simplified diagrams.

---

## Getting started

### 1. Prerequisites

- Python 3.13 (`brew install python@3.13`)
- Node.js 20+ (already installed if you can run `node -v`)
- PostgreSQL (`brew install postgresql@17`)

### 2. Get your API keys

Three keys are required to run analyses. All have free tiers and none require a credit card to start (except OpenAI, which is pay-as-you-go but cheap per request).

| Service | What it's for | Where to get it | Free tier |
|---|---|---|---|
| **OpenAI** | Claim extraction, language/bias analysis, evidence comparison (structured JSON output) | https://platform.openai.com/api-keys — sign up, add a bit of billing credit, click "Create new secret key" | Pay-as-you-go; cheap per request (GPT-5.6 Sol: ~$5/$30 per 1M tokens) |
| **Firecrawl** | Turns article URLs into clean markdown + metadata | https://www.firecrawl.dev/app — sign up, copy your key from the dashboard | 1,000 free credits/month, no card required. Also works keyless (rate-limited), fine for quick tests |
| **Exa** | Searches the web for independent coverage of a story/claim | https://dashboard.exa.ai/api-keys — sign up (Google or email), copy your key | New accounts get $20 free credit, no card required |

Put them in `backend/.env` (see step 4). **Never commit `.env` files** — `.gitignore` already excludes them.

Two more are optional — the app works fully without them, and those features simply stay hidden until configured:

| Service | What it's for | Where to get it | Free tier |
|---|---|---|---|
| **ElevenLabs** | ~30s spoken audio summary of the Story Profile | https://elevenlabs.io → Profile → API Keys | ~10,000 characters/month, no card required |
| **fal.ai** | Soft "does the lead image look AI-generated?" heuristic | https://fal.ai → Dashboard → Keys | ~$1 free credit on signup |

### 3. Database setup

```bash
brew services start postgresql@17
createdb storylens
```

### 4. Backend setup

```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit backend/.env and paste in your OPENAI_API_KEY, FIRECRAWL_API_KEY, EXA_API_KEY
```

Run it:

```bash
uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on startup (`Base.metadata.create_all` — no migration tool). Visit http://localhost:8000/docs for interactive API docs.

### 5. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env   # defaults to VITE_API_URL=http://localhost:8000, adjust if needed
npm run dev
```

Visit http://localhost:5173.

### 6. Use it

Paste a real article URL (Reuters, AP, BBC, a smaller outlet, etc.) and click **Analyze**. The first request takes ~20–60 seconds because the backend extracts the article, calls the LLM twice, searches Exa, and scrapes up to 5 related articles with Firecrawl. Re-analyzing the same URL within 6 hours returns instantly from cache (see [Optional features](#optional-features) below).

You can drag the "Adjust weights" sliders on the Story Profile to see the Trust Score recompute live (the frontend mirrors the exact same weighted-sum formula as the backend engine).

---

## How the Trust Score is computed

`backend/app/scoring.py` combines five 0-100 sub-scores with configurable weights (defaults: 25% source reliability, 30% corroboration, 25% evidence quality, 10% headline/body consistency, 10% anti-sensationalism):

- **Source reliability** — looked up from a small curated table of ~40 well-known outlets (`seed_sources.py`). Unknown domains get a neutral default (50). This is a directional signal, not a fact about the outlet.
- **Corroboration** — counts *independent* outlets covering the story. Related articles are clustered by domain and by near-duplicate text (via `difflib`) so that multiple sites copying the same wire story don't count as independent corroboration.
- **Evidence quality** — importance- and confidence-weighted average of per-claim verdicts (supported / partially_supported / unverified / contradicted), further weighted by the reliability of the citing sources (a claim "supported" by Reuters counts more than one "supported" by an unknown blog).
- **Headline/body consistency** and **sensationalism** — signals produced by the LLM, passed through as-is (they are sub-signals, not the final score).

The LLM never outputs a final Trust Score — only these sub-signals feed a plain-Python weighted average.

---

## Optional features

- **Caching by URL** (`routers/analyze.py::_cached_profile`) — re-analyzing the same article within 6 hours reconstructs the Story Profile straight from Postgres instead of re-calling Firecrawl/Exa/OpenAI. No extra API key needed. Custom weight overrides still recompute the Trust Score live even on a cached hit. A "Cached result" badge appears in the UI.
- **Spoken audio summary** — click "Listen to summary" to hear a ~30s ElevenLabs narration of the Story Profile summary. Generated on first request, then cached to disk (`backend/.audio_cache/`, gitignored). Requires `ELEVENLABS_API_KEY`; the button simply doesn't render if it's not configured.
- **AI-generated-image heuristic** — a soft 0-100 "does the lead image look AI-generated?" signal using a hosted vision LLM (`fal-ai/any-llm/vision`), always shown with an explicit disclaimer that it's a rough heuristic, not a forensic verdict. Requires `FAL_API_KEY`; the card simply doesn't render if it's not configured or no lead image was found.

---

## Deployment

Config files (`render.yaml`, `netlify.toml`) are already in the repo root. Full step-by-step instructions: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

Short version: backend + Postgres on Render (`render.yaml` blueprint), frontend on Netlify (`netlify.toml`), no Docker for either.

---

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
    routers/analyze.py          POST /analyze orchestration endpoint + caching + audio-summary
    services/
      firecrawl_client.py       Article extraction (+ lead image for the AI-image signal)
      exa_client.py             Independent-coverage search
      elevenlabs_client.py      Optional: text -> spoken audio summary
      fal_client.py             Optional: soft AI-generated-image heuristic (vision LLM)
      llm/
        base.py                 Abstract LLMProvider interface (swap providers later)
        openai_provider.py      OpenAI implementation (Structured Outputs)
        schemas.py               Pydantic schemas for LLM structured output
        prompts.py               Prompt text for both LLM passes
  requirements.txt
  .env.example

frontend/
  src/
    App.tsx                     Top-level page: input -> loading -> Story Profile
    api.ts                      POST /analyze client + audio-summary URL helper
    scoring.ts                  Client-side mirror of the weighted-sum formula (for live sliders)
    types.ts                    TypeScript types matching backend schemas.py
    assets/logo.svg             App logo (also used as favicon)
    components/
      UrlInputForm.tsx
      LoadingSteps.tsx
      TrustScoreGauge.tsx
      SubscoreBars.tsx           Sub-score bars + adjustable weight controls
      WeightSlider.tsx           Custom click/drag/button weight control (not a native <input range>)
      ArticleHeader.tsx          Title/source/author/date + political framing signal
      ReasonsWarnings.tsx
      ClaimsList.tsx
      OutletFraming.tsx
      RelatedSources.tsx
      AudioSummary.tsx           Lazy-loaded ElevenLabs audio player
      AiImageSignal.tsx          Soft AI-image-likelihood card
      StoryProfile.tsx           Composes all of the above
  .env.example
```

---

## Non-goals

By design, this project does not include: Docker, a database migration tool, user accounts, a browser extension, a from-scratch ML model, a comprehensive global source-rating database, a dedicated AI-image forensics system, or any claim of definitively "fake" vs "real". Richer source history and authentication are unimplemented follow-ups beyond current scope.

Authored by: Andrej Ristikj and Maksim Kirandjiski