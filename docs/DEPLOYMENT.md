# Deploying StoryLens

Backend on **Render**, frontend on **Netlify**, Postgres on **Render**. No
Docker needed for either.

Config files already in the repo root:

- `render.yaml` - Render Blueprint (web service + Postgres database)
- `netlify.toml` - Netlify build config for the `frontend/` subdirectory

There's a bit of a chicken-and-egg problem (backend needs to know the
frontend's URL for CORS, frontend needs to know the backend's URL to call
it), so deploy in this order:

## 1. Push to GitHub

Render and Netlify both deploy from a Git repo. This repo already has a
remote configured:

```bash
git push origin main
```

## 2. Deploy the backend on Render

1. Go to [dashboard.render.com](https://dashboard.render.com) -> **New** ->
   **Blueprint**.
2. Connect your GitHub account/repo (`storylens`) if you haven't already.
3. Render will detect `render.yaml` and show you the `storylens-api` web
   service and `storylens-db` Postgres database it's about to create. Click
   **Apply**.
4. Once created, open the `storylens-api` service -> **Environment** and
   fill in the three secret values left blank in `render.yaml`:
   - `OPENAI_API_KEY`
   - `FIRECRAWL_API_KEY`
   - `EXA_API_KEY`
5. Wait for the first deploy to finish, then copy the service URL Render
   gives you, e.g. `https://storylens-api.onrender.com`. This is your
   backend URL - use it in step 3.
6. Tables are created automatically on startup (`Base.metadata.create_all`)
   - no manual migration step needed.

**Note:** Render's free web service tier spins down when idle and takes
~30-60s to wake up on the next request. Fine for a demo, just don't be
surprised by the first request being slow after inactivity. Consider
upgrading the plan before a live demo if that matters.

## 3. Deploy the frontend on Netlify

1. Go to [app.netlify.com](https://app.netlify.com) -> **Add new site** ->
   **Import an existing project** -> connect GitHub -> select the
   `storylens` repo.
2. Netlify should auto-detect `netlify.toml` (base directory `frontend`,
   build command `npm run build`, publish directory `dist`). Confirm those
   settings if prompted.
3. Before the first deploy (or right after, then redeploy), go to **Site
   configuration -> Environment variables** and add:
   - `VITE_API_URL` = the Render backend URL from step 2 (e.g.
     `https://storylens-api.onrender.com`)
4. Deploy. Copy the resulting Netlify URL, e.g.
   `https://storylens.netlify.app`.

## 4. Close the loop: update backend CORS

1. Back in Render, open `storylens-api` -> **Environment**, update
   `CORS_ORIGINS` to your real Netlify URL from step 3 (comma-separate if
   you also want to allow a custom domain later), e.g.:
   ```
   CORS_ORIGINS=https://storylens.netlify.app
   ```
2. Save - Render will redeploy the service automatically.

## 5. Verify

- Visit your Netlify URL, paste a real article URL, click Analyze.
- If you get a CORS error in the browser console, double-check
  `CORS_ORIGINS` on Render exactly matches the Netlify origin (no trailing
  slash).
- If the first request times out, it's likely Render's free-tier cold
  start - wait ~30s and retry.

## Custom domains (optional)

Both Render and Netlify support adding a custom domain from their
dashboards (Render: service -> Settings -> Custom Domains; Netlify: Site
configuration -> Domain management). Update `CORS_ORIGINS` and
`VITE_API_URL` again if you add one.

## Troubleshooting

- **`psycopg.OperationalError: [Errno -2] Name or service not known`** on
  startup: the web service and the database are in different Render regions.
  Render's internal DNS (used by the `DATABASE_URL` injected via
  `fromDatabase`) only resolves between services in the *same* region -
  across regions the short internal hostname just doesn't resolve.
  `render.yaml` now pins the database to `region: frankfurt` to match the web
  service. If you already applied the blueprint before this fix, the
  database was likely created in Render's default region (not Frankfurt) -
  region can't be changed after creation, so delete the `storylens-db`
  database (and the web service, to be safe) in the Render dashboard and
  re-apply the blueprint from scratch so both are created in Frankfurt
  together.
- **`pip` fails with `metadata-generation-failed` on `pydantic-core`** during
  the Render build: this means Render picked a Python version too new for
  `pydantic-core` to have a prebuilt wheel (it's a Rust extension, and the
  build image has no Rust toolchain to compile it from source). Render's
  default runtime jumped to Python 3.14 in Feb 2026, which is too new for
  our pinned dependencies. `render.yaml` already sets `PYTHON_VERSION=3.13.15`
  for exactly this reason - if you set the service up manually instead of via
  the blueprint, add that env var (or rely on the `.python-version` file
  already present in `backend/`) yourself.
