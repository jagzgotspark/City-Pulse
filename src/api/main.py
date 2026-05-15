from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.utils.database import init_db

app = FastAPI(
    title="City Pulse API",
    description="Real-time city pulse scores",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"status": "City Pulse API is running"}