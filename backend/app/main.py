from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db.database import init_db, get_db
from app.modules.auth.api import router as auth_router
from app.modules.employers.api import router as employer_router
from app.modules.employees.api import router as employee_router
from app.utils.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    # 1. Initialize DB tables
    try:
        await init_db()
    except Exception as e:
        print(f"Error initializing DB tables: {e}")
        
    # 2. Connect to Redis
    redis_client.connect()
    
    yield
    
    # Shutdown actions
    await redis_client.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="SaaS Platform for Bangladesh Income Tax Management",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint to monitor API, database, and cache readiness."""
    health_status = {
        "status": "healthy",
        "services": {
            "api": "online",
            "database": "offline",
            "cache": "offline"
        }
    }
    
    # Test DB Connection
    try:
        await db.exec(select(1))
        health_status["services"]["database"] = "online"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = f"error: {str(e)}"
        
    # Test Redis Connection
    try:
        if redis_client.client:
            # Simple ping
            await redis_client.client.ping()
            health_status["services"]["cache"] = "online"
        else:
            health_status["services"]["cache"] = "not_connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["cache"] = f"error: {str(e)}"
        
    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
        
    return health_status


# Register Router
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth")
app.include_router(employer_router, prefix=f"{settings.API_V1_STR}/employers")
app.include_router(employee_router, prefix=f"{settings.API_V1_STR}/employees")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
