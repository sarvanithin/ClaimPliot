from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import routes

app = FastAPI(
    title="ClaimPilot API",
    description="AI Prior Authorization Appeal Agent",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. In prod, specify the exact domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to ClaimPilot API"}
