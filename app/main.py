from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Learn with Jiji API",
    description="AI Learning Companion Backend Service",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["Jiji"])

@app.get("/")
async def root():
    return {"message": "Welcome to Learn with Jiji API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
