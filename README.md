# 🌆 City Pulse

> Real-time city energy scores powered by multi-source data aggregation and AI

**Live demo:** https://your-vercel-url.vercel.app  
**API docs:** https://city-pulse-production-5856.up.railway.app/docs

---

## What is it?

City Pulse tracks the real-time "energy" of Indian cities by aggregating 
weather, air quality, and event data into a single pulse score (0–100). 
An LLM generates a one-sentence human-readable mood summary for each city, 
updated every 15 minutes automatically.

---

## Architecture

Data Sources → Python Ingestion Pipeline → PostgreSQL → FastAPI → React

- **Ingestion:** APScheduler fetches from 3 APIs every 15 minutes
- **Scoring:** Weighted algorithm combining weather, air quality, and events
- **API:** FastAPI serves 5 REST endpoints with Pydantic validation
- **Summaries:** Groq (Llama3) generates city mood summaries with 30min caching
- **Frontend:** React with Recharts visualisations, auto-refreshes every 60s

---

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, APScheduler  
**Frontend:** React, Recharts, Axios  
**AI:** Groq API (Llama3-8b)  
**Data:** OpenWeatherMap, PredictHQ, OpenWeatherMap Air Pollution  
**Deploy:** Railway (backend + DB), Vercel (frontend)

---

## Scoring Algorithm

Pulse score is a weighted combination of three sub-scores:

- **Weather (X%):** Scores temperature comfort, humidity, wind, sky condition
- **Air Quality (X%):** Maps AQI 1–5 to 0–100, heavily penalises AQI 4–5
- **Events (X%):** More active events = higher city energy

[Write your actual weights and logic here]

---

## Running Locally

\`\`\`bash
git clone https://github.com/jagzgotspark/City-Pulse
cd City-Pulse
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your API keys
python3 main.py       # single collection run
python3 -m src.scheduler  # continuous pipeline
uvicorn src.api.main:app --reload  # start API
\`\`\`