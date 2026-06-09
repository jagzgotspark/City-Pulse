# 🌆 City Pulse

A real-time city analytics platform that transforms weather, air quality, and event data into a single Pulse Score (0–100), helping users understand how vibrant, comfortable, and active a city feels at any moment.

Built using FastAPI, PostgreSQL, React, Redis, FAISS, Prophet forecasting, and AI-generated city mood summaries.

---

## 🚀 Live Demo

**Frontend:** https://project-s9n4g.vercel.app

**Backend API:** https://city-pulse-production-5856.up.railway.app

---

## ✨ Features

- Real-time weather, air quality, and event monitoring
- Custom Pulse Score algorithm with live-tunable weights
- Neighbourhood-level drill-down (Hazratganj vs Gomti Nagar, Bandra vs Colaba)
- FAISS embedding similarity — "which cities feel like Bengaluru right now?"
- AI-generated city mood summaries via Groq Llama3
- 24-hour forecasting with Facebook Prophet and confidence intervals
- City vs City head-to-head comparison
- Real AQI using EPA PM2.5 formula (not OWM's 1–5 index)
- WebSocket push — dashboard refreshes automatically on new data
- Redis caching — survives server restarts, shared across requests
- Admin dashboard — tune scoring weights live without redeployment
- Shareable city vibe card (Canvas API → PNG download)
- PWA — installable on mobile, offline fallback via service worker
- Automated data collection every 15 minutes for all tracked cities

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                       Frontend                           │
│         React + Leaflet + Recharts (Vercel)              │
│   Leaderboard · Map · Cards · Trends · Forecasts        │
└────────────────────────┬────────────────────────────────┘
                         │ REST + WebSocket
┌────────────────────────▼────────────────────────────────┐
│                    FastAPI Backend (Railway)              │
│                                                          │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐  │
│  │  APScheduler │  │  11 Routes  │  │   WebSocket    │  │
│  │ every 15 min │  │             │  │  push on update│  │
│  └──────┬───────┘  └──────┬──────┘  └────────────────┘  │
│         │                 │                              │
│  ┌──────▼─────────────────▼──────────────────────────┐  │
│  │   PostgreSQL · Redis cache · FAISS vectors         │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│          OpenWeatherMap · Ticketmaster · Groq            │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

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

## 📊 Pulse Score Algorithm

```text
Pulse Score =
  (Weather Score  × 0.50)
+ (Air Score      × 0.35)
+ (Events Score   × 0.15)

Hard cap: AQI 5 → max 45 · AQI 4 → max 65
```

Weights are tunable live via the admin dashboard without redeployment.

### Weather Score
Temperature comfort (ideal 22–28°C for India), humidity, wind speed, sky condition.

### Air Quality Score
Raw PM2.5 → EPA AQI formula → mapped to 0–100.

### Events Score
Active event count via Ticketmaster API → city activity level.

---

## 🔧 Key Engineering Decisions

**APScheduler inside FastAPI instead of a separate cron service**
Railway's free tier doesn't support cron jobs. Running APScheduler as a daemon thread inside the FastAPI process means the scheduler stays alive as long as the web service does — zero extra services, zero extra cost.

**FAISS for similar city search instead of SQL distance queries**
SQL threshold queries on multi-dimensional vectors don't capture proximity well. FAISS does L2 nearest-neighbour search across all city vectors in microseconds, and produces meaningfully more accurate similarity results.

**Redis instead of in-memory caching**
The original cache was a Python dict that reset on every Railway restart. Groq summaries cost API calls and take ~2 seconds each. Redis survives restarts, is shared across requests, and reduces Groq calls by ~80% in practice.

**Prophet for forecasting instead of simpler models**
Prophet handles daily seasonality in city data without manual feature engineering. It also produces 80% confidence intervals out of the box — users see uncertainty, not just a line.

**OWM geocoding before weather fetch**
OWM's city name search has ambiguity issues ("Manali" returns Tamil Nadu, not Himachal Pradesh). Using OWM's geocoding API first resolves to correct coordinates via state metadata before any weather fetch.

---

## 🤖 AI Mood Summaries

City Pulse uses Llama3 through the Groq API to generate natural-language descriptions of a city's current atmosphere, cached in Redis for 30 minutes.

> *"Mumbai basks in warm, crystal-clear serenity, alive and thriving tonight."*

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard` | All cities with scores, AQI, summaries |
| GET | `/api/pulse/{city}` | Single city latest data |
| GET | `/api/search/{city}` | On-demand fetch + persist any city |
| GET | `/api/trend/{city}` | Hourly pulse trend (1–30 days) |
| GET | `/api/forecast/{city}` | Prophet 24h forecast |
| GET | `/api/neighbourhood/{city}` | Grid-level scores within a city |
| GET | `/api/similar/{city}` | FAISS nearest-neighbour cities |
| GET | `/api/comparison` | 7-day city ranking |
| POST | `/api/admin/weights` | Update scoring weights live |
| GET | `/api/admin/stats` | Collection stats and data point counts |
| WS | `/ws/dashboard` | WebSocket push on each collection run |

---

## 🗄 Database Schema

`cities` — tracked cities with coordinates

`weather_snapshots` — weather observations every 15 min

`air_quality_snapshots` — AQI and PM2.5 measurements

`events_snapshots` — event activity data

`pulse_scores` — calculated scores and AI summaries

`neighbourhood_snapshots` — grid-level scores per city area

`city_vectors` — FAISS feature vectors for similarity search

---

## ⚙️ Local Setup

```bash
git clone https://github.com/jagzgotspark/City-Pulse.git
cd City-Pulse
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENWEATHER_API_KEY=your_key
TICKETMASTER_API_KEY=your_key
GROQ_API_KEY=your_key
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url
ADMIN_PASSWORD=your_password
```

Start the server:

```bash
uvicorn src.api.main:app --reload
```

The scheduler starts automatically with the server. To run it manually against a remote DB:

```bash
DATABASE_URL=your_railway_url python3 -m src.scheduler
```

---

## 🎯 Engineering Challenges Solved

- Designed a weighted scoring algorithm that models city livability and activity
- Built an automated multi-source ingestion pipeline across weather, AQI, and events APIs
- Resolved city name ambiguity using OWM geocoding before coordinate-based fetches
- Implemented neighbourhood-level data collection using lat/lon grid points
- Replaced in-memory cache with Redis for persistence across Railway restarts
- Built FAISS vector similarity search for real-time city recommendations
- Integrated WebSocket broadcasting to push live updates to connected clients
- Managed time-series analytics and ML forecasting on continuously collected data

---

## 👩‍💻 Author

**Jagriti Singh** · 3rd Year CSE-AIML · VIT Chennai

Built as a full-stack data engineering, analytics, and machine learning project focused on transforming raw city data into meaningful real-time insights.