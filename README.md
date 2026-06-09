# City Pulse

**Live city energy scores across India — real-time, every 15 minutes.**

[**Live Demo →**](https://project-s9n4g.vercel.app) · [API](https://city-pulse-production-5856.up.railway.app)

---

## What it does

City Pulse aggregates weather, air quality, and event data for Indian cities into a single **pulse score** (0–100) — a composite measure of how liveable and energetic a city feels right now. Scores update every 15 minutes via a background scheduler running 24/7 on Railway.

You can search any city in India, compare cities head-to-head, drill into neighbourhood-level scores, see a 24-hour Prophet forecast, and share a city's vibe as a downloadable card.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Frontend                          │
│         React + Leaflet + Recharts (Vercel)              │
│   Leaderboard · Map · Cards · Trends · Forecasts        │
└────────────────────────┬────────────────────────────────┘
                         │ REST + WebSocket
┌────────────────────────▼────────────────────────────────┐
│                      FastAPI Backend                     │
│                      (Railway)                           │
│                                                          │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │  Scheduler   │  │   Routes    │  │   WebSocket    │  │
│  │ APScheduler  │  │  11 endpoints│  │  /ws/dashboard │  │
│  │ every 15 min │  │             │  │  push on update│  │
│  └──────┬───────┘  └──────┬──────┘  └────────────────┘  │
│         │                 │                              │
│  ┌──────▼─────────────────▼──────────────────────────┐  │
│  │              Data Layer                            │  │
│  │  PostgreSQL · Redis cache · FAISS vectors          │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   External APIs                          │
│   OpenWeatherMap · Ticketmaster · Groq (Llama3)          │
└─────────────────────────────────────────────────────────┘
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Scheduling | APScheduler (background thread inside FastAPI) |
| Database | PostgreSQL |
| Cache | Redis |
| ML | Facebook Prophet (forecasting), FAISS (similarity search) |
| AI summaries | Groq API — Llama3 |
| Frontend | React, Recharts, Leaflet |
| Deploy | Railway (backend + DB + Redis), Vercel (frontend) |

---

## Key technical decisions

**Why APScheduler inside FastAPI instead of a separate cron service?**
Railway's free tier doesn't support cron jobs. Running APScheduler as a daemon thread inside the FastAPI process means the scheduler stays alive as long as the web service does — zero extra services, zero extra cost. The tradeoff is that a crash of the web process kills the scheduler too, but Railway's auto-restart handles that.

**Why FAISS for similar city search instead of a SQL query?**
SQL distance queries on 5-dimensional vectors (`WHERE ABS(pulse_score - x) < threshold AND ...`) don't scale and don't capture multi-dimensional proximity well. FAISS does L2 nearest-neighbour search across all city vectors in microseconds, and the result ("Mumbai and Bengaluru have a similar vibe right now") is meaningfully more accurate than a threshold-based approach.

**Why Redis instead of in-memory caching?**
The original cache was a Python dict — it reset on every Railway restart. Groq LLM summaries cost API calls and take ~2 seconds each. With 15 cities generating summaries every 30 minutes, cold starts were slow and expensive. Redis survives restarts, is shared across requests, and reduces Groq calls by ~80% in practice.

**Why Prophet for forecasting instead of a simpler model?**
Prophet handles the seasonality patterns in city data (daily temperature cycles, rush hour activity) without requiring manual feature engineering. It also produces 80% confidence intervals out of the box, which makes the forecast chart more honest — users see the uncertainty, not just a line.

**Why OWM geocoding before weather fetch?**
OpenWeatherMap's city name search has ambiguity issues — "Manali" returns Manali, Tamil Nadu instead of Manali, Himachal Pradesh. Using OWM's geocoding API first (`/geo/1.0/direct`) returns ranked results with state metadata, so we can resolve to the correct coordinates before fetching weather. All weather is then fetched by lat/lon, not city name.

---

## Features

- **Live leaderboard** — all tracked cities ranked by pulse score, updating every 15 minutes
- **Neighbourhood drill-down** — zoom into a city on the map to see pulse scores by area (Hazratganj vs Gomti Nagar in Lucknow, Bandra vs Colaba in Mumbai)
- **Similar city search** — FAISS embedding similarity: "which cities feel like Bengaluru right now?"
- **24h Prophet forecast** — ML model trained on historical pulse scores with confidence intervals
- **City vs City comparison** — head-to-head on pulse score, temperature, AQI, weather score, air score
- **AI mood summaries** — Groq Llama3 generates a one-line vibe description per city
- **Real AQI** — EPA PM2.5 formula applied to raw sensor data, not OWM's 1–5 index
- **Admin dashboard** — password-gated page to tune scoring weights live and monitor data collection
- **PWA** — installable on mobile, service worker for offline fallback
- **WebSocket push** — dashboard refreshes automatically when new data arrives, no polling
- **Shareable city card** — Canvas API generates a downloadable PNG of any city's pulse

---

## Scoring algorithm

```python
pulse_score = (
    weather_score  * 0.50 +   # temperature comfort, humidity, condition, wind
    air_score      * 0.35 +   # PM2.5 → EPA AQI → 0-100 mapping
    events_score   * 0.15     # active event count via Ticketmaster API
)
# hard cap: AQI 5 → max score 45, AQI 4 → max score 65
```

Weights are tunable live via the admin dashboard without redeployment.

---

## API endpoints

```
GET  /api/dashboard              All cities with scores, AQI, summaries
GET  /api/pulse/{city}           Single city latest data
GET  /api/search/{city}          On-demand fetch + persist any city
GET  /api/trend/{city}           Hourly pulse trend (1–30 days)
GET  /api/forecast/{city}        Prophet 24h forecast
GET  /api/neighbourhood/{city}   Grid-level pulse scores within a city
GET  /api/similar/{city}         FAISS nearest-neighbour cities
GET  /api/comparison             7-day city ranking
GET  /api/admin/weights          Current scoring weights (password-gated)
POST /api/admin/weights          Update scoring weights live
GET  /api/admin/stats            Collection stats and data point counts
WS   /ws/dashboard               WebSocket — push on each collection run
```

---

## Local setup

```bash
git clone https://github.com/jagzgotspark/City-Pulse
cd City-Pulse
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# copy and fill in your keys
cp .env.example .env

# init DB and start scheduler + server
uvicorn src.api.main:app --reload
```

Required env vars: `OPENWEATHER_API_KEY`, `GROQ_API_KEY`, `TICKETMASTER_API_KEY`, `DATABASE_URL`, `REDIS_URL`

---

## Project structure

```
src/
  api/          FastAPI app, routes, cache, WebSocket, LLM
  fetchers/     Weather, air quality, events, neighbourhood ingestion
  ml/           Prophet forecasting, FAISS similarity
  scoring/      Weighted pulse score engine
  utils/        Database functions, data transforms, AQI formula
  scheduler.py  APScheduler — collects all cities every 15 min
```

---

Built by Jagriti Singh · 3rd year CSE-AIML · VIT Chennai