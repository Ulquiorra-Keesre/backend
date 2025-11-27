# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routes import auth, chats, items, users
from src.database.connection import create_tables
from src.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    print("✅ Database tables created")
    yield
    # Shutdown
    print("🛑 Application shutdown")

app = FastAPI(
    title="Rent System API",
    description="Backend for a peer-to-peer rental platform with chat",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(chats.router, prefix="/api/chats", tags=["Chats"])

@app.get("/")
async def root():
    return {"message": "Система студенческих опросов API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)