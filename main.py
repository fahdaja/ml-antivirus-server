from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Imports for database and models
from app.db.database import engine, Base
# Import models to ensure they are registered with Base metadata
from app.features.scans.model import Scan, ScanResult  
from app.features.scans.router import router as scans_router

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MangoDefend ML Antivirus Backend",
    description="Backend API for MangoDefend Malware Scanner",
    version="1.0.0"
)

# Set up CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect all application routers here
app.include_router(scans_router)

@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "Welcome to MangoDefend API! System is up and running."
    }

if __name__ == "__main__":
    # Point this to run the server in development mode
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
