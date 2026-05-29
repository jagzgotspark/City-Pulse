# 🌆 City Pulse

A real-time city analytics platform that transforms weather, air quality, and event data into a single Pulse Score (0–100), helping users understand how vibrant, comfortable, and active a city feels at any moment.

Built using FastAPI, PostgreSQL, React, machine learning forecasting, and AI-generated city mood summaries.

---

## 🚀 Live Demo

**Frontend:** https://project-s9n4g.vercel.app

**Backend API:** https://city-pulse-production-5856.up.railway.app

---

## ✨ Features

- Real-time weather monitoring
- Air quality tracking and AQI analysis
- Event density monitoring
- Custom Pulse Score algorithm
- AI-generated city mood summaries using Llama 3
- Historical trend analysis
- 24-hour forecasting with Facebook Prophet
- Interactive city search
- Automated data collection every 15 minutes
- PostgreSQL time-series storage

---

## 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │  OpenWeather API │
                    └─────────┬────────┘
                              │
                    ┌─────────▼────────┐
                    │ Air Quality API  │
                    └─────────┬────────┘
                              │
                    ┌─────────▼────────┐
                    │   PredictHQ API  │
                    └─────────┬────────┘
                              │

                    ┌─────────▼────────┐
                    │ APScheduler Job  │
                    │ (Every 15 mins)  │
                    └─────────┬────────┘
                              │

                    ┌─────────▼────────┐
                    │ Data Processing  │
                    │ & Transformation │
                    └─────────┬────────┘
                              │

                    ┌─────────▼────────┐
                    │ Pulse Score      │
                    │ Calculation      │
                    └─────────┬────────┘
                              │

                    ┌─────────▼────────┐
                    │ PostgreSQL       │
                    │ Time-Series DB   │
                    └─────────┬────────┘
                              │

                    ┌─────────▼────────┐
                    │ FastAPI Backend  │
                    └─────────┬────────┘
                              │

          ┌───────────────────▼───────────────────┐
          │ React Dashboard + Charts + Maps + AI │
          └───────────────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- APScheduler

### Frontend

- React
- Axios
- Recharts
- Leaflet

### AI & Machine Learning

- Groq API (Llama 3)
- Facebook Prophet

### Deployment

- Railway
- Vercel

---

## 📊 Pulse Score Algorithm

The Pulse Score is a weighted combination of multiple city indicators.

### Weather Score

Factors considered:

- Temperature comfort
- Humidity
- Wind speed
- Weather conditions

### Air Quality Score

Factors considered:

- AQI
- PM2.5 concentration
- Pollution severity

### Event Score

Factors considered:

- Number of local events
- City activity level

### Final Score

```text
Pulse Score =
(Weather Score × Weight)
+ (Air Quality Score × Weight)
+ (Event Score × Weight)
```

Scores are normalized and constrained between 0 and 100.

---

## 🤖 AI Mood Summaries

City Pulse uses Llama 3 through the Groq API to generate natural-language descriptions of a city's current atmosphere.

Example:

> "Lucknow feels lively this evening with pleasant weather, moderate air quality, and several ongoing events contributing to a vibrant city vibe."

To reduce latency and API costs, generated summaries are cached for 30 minutes.

---

## 📈 Forecasting

The platform uses Facebook Prophet to forecast city Pulse Scores for the next 24 hours.

Features:

- Daily seasonality detection
- Confidence intervals
- Historical trend learning
- Cached forecasts for faster responses

---

## 🗄 Database Schema

### cities

Stores tracked cities.

### weather_snapshots

Stores weather observations collected every 15 minutes.

### air_quality_snapshots

Stores AQI and pollutant measurements.

### events_snapshots

Stores event activity data.

### pulse_scores

Stores calculated Pulse Scores and AI summaries.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|----------|----------|-------------|
| GET | `/api/dashboard` | All tracked cities |
| GET | `/api/pulse/{city}` | Latest city data |
| GET | `/api/search/{city}` | Search and save a city |
| GET | `/api/trend/{city}` | Historical trends |
| GET | `/api/history/{city}` | Weather and AQI history |
| GET | `/api/daily/{city}` | Daily summary |
| GET | `/api/comparison` | City rankings |
| GET | `/api/forecast/{city}` | 24-hour forecast |
| GET | `/api/forecast` | Forecasts for all cities |

---

## ⚙️ Local Setup

### Clone Repository

```bash
git clone https://github.com/jagzgotspark/City-Pulse.git
cd City-Pulse
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
OPENWEATHER_API_KEY=your_key
PREDICTHQ_TOKEN=your_token
GROQ_API_KEY=your_key
DATABASE_URL=your_database_url
```

### Start Backend

```bash
uvicorn src.api.main:app --reload
```

### Start Scheduler

```bash
python3 -m src.scheduler
```

---

## 🎯 Engineering Challenges Solved

- Designed a weighted scoring algorithm that models city livability and activity
- Built an automated multi-source ingestion pipeline
- Managed time-series analytics using PostgreSQL
- Integrated AI-generated summaries while minimizing latency through caching
- Implemented machine learning forecasting on continuously collected city data
- Built on-demand city discovery and persistence

---

## 📌 Future Improvements

- Neighborhood-level analytics
- More environmental indicators
- User personalization
- Advanced forecasting models
- Real-time alerting system

---

## 👩‍💻 Author

**Jagriti Singh**

Built as a full-stack data engineering, analytics, and machine learning project focused on transforming raw city data into meaningful real-time insights.