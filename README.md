# Wind Forecast Decision Desk

A pilot dashboard for reviewing Elexon GB wind generation forecasts available at a day-ahead decision cutoff and comparing those forecasts with generation outturn.

## Project Layout

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI route handlers
│   │   ├── data/                # Elexon client, retry policy, and data cache
│   │   ├── domain/              # Analysis-window value object
│   │   ├── services/            # Interval analysis and dashboard assembly
│   │   ├── config.py            # Environment-backed application settings
│   │   └── main.py              # FastAPI app and middleware setup
│   ├── tests/                   # Forecast selection, aggregation, and metric tests
│   ├── credentials.env.example # Safe local configuration defaults
│   ├── Dockerfile
│   ├── pyproject.toml           # uv dependencies and pytest configuration
│   └── uv.lock                  # Reproducible Python dependency lock
├── frontend/
│   ├── src/
│   │   ├── components/          # Dashboard controls, chart, metrics, and tables
│   │   ├── hooks/               # Dashboard API lifecycle
│   │   ├── lib/                 # Display formatting helpers
│   │   ├── App.tsx              # Page composition
│   │   └── styles.css           # Reint-inspired design tokens and layout
│   ├── .env.example             # Frontend API URL
│   ├── Dockerfile
│   ├── package.json
│   └── package-lock.json
├── docker-compose.yml
└── .gitignore
```

## Start With Docker

Create the ignored local environment file from the example:

```sh
cp backend/credentials.env.example backend/credentials.env
```

Then start both services:

```sh
docker compose up --build
```

Open the dashboard at `http://localhost:5173`. The API health check is at `http://localhost:8000/api/health`; its interactive API docs are at `http://localhost:8000/docs`.

## Start Without Docker

Backend, from the repository root:

```sh
cd backend
uv sync --dev
uv run uvicorn app.main:app --reload
```

Frontend, in a second terminal from the repository root:

```sh
cd frontend
cp .env.example .env
npm install
npm run dev
```

The frontend example defaults to the local API at `http://localhost:8000`. Set `VITE_API_URL` in `frontend/.env` if the API is hosted elsewhere. The dashboard follows Reint AI's public white, charcoal, and green brand palette.

## Data and Analysis

- Uses only Elexon BMRS `WINDFOR` forecasts and `FUELHH` actuals where `fuelType=WIND`.
- The pilot window is decision dates January 1–31, 2026; next-day deliveries extend from January 2 through February 1.
- Forecast selection uses the latest `publishTime` no later than the selected Europe/London decision cutoff. The default cutoff is 10:00 and is a pilot assumption, not a confirmed client rule.
- `WINDFOR` values are hourly. `FUELHH` values are half-hourly average MW, so actuals are averaged in complete pairs for hourly comparison. Incomplete pairs are excluded.
- Forecast error is forecast minus actual. The dashboard reports MAE, RMSE, signed mean bias, and matched interval coverage.
- Wind generation alone does not determine a utility's total procurement requirement. Demand, other generation, prices, and portfolio positions are out of scope.

The decision date range, default cutoff, Elexon API base URL, local CORS origin, request timeout, retry/backoff, and cache TTL are configurable in `backend/credentials.env`. Keep this file local; it is ignored by Git. No API key is required for the public Elexon endpoints used by this pilot.

The Elexon client keeps its base URL, request timeout, retry count/backoff, and per-window cache TTL in one `ElexonClient` instance, so transport policy can be configured or tested independently from the dashboard logic.

## Tests

```sh
cd backend
uv run pytest -q
```

## Vercel Deployment

The root `vercel.json` defines a Vercel Services deployment with two services. Import the repository with its root directory set to the repository root. Requests under `/api/` route to the FastAPI backend; all other paths route to the Vite frontend. The backend is public only through `/api/*` and does not need a service binding because the browser calls it through the shared public origin.

In Vercel project environment settings, configure `DECISION_START_DATE`, `DECISION_END_DATE`, and `DECISION_CUTOFF_TIME` for the pilot window. `ELEXON_API_BASE_URL` is optional and defaults to the public BMRS API. Do not set `VITE_API_URL` for the Vercel deployment: the production frontend uses the same-origin `/api` route. Keep `frontend/.env` for local development, where it points directly to `http://localhost:8000`.

Test the services locally from the repository root with:

```sh
vercel dev -L
```

Deployment is not published yet. After deployment, add the public Vercel URL here and verify it, the public GitHub repository, and the unlisted demo video in a signed-out/incognito session before submitting the form.

The demo recording should contain a customer walkthrough and a technical review, each no longer than five minutes, with a total duration under ten minutes.

## AI Tool Disclosure

This project utilized AI assistance (GitHub Copilot) for:
- Rapid boilerplate creation for FastAPI endpoints and React/Tailwind components.
- Docker & Docker Compose configuration drafting.
- Documentation and docstring for python functions.
- Self review for the code written to adhere to best coding practises.