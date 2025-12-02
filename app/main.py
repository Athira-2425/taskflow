"""
Main FastAPI application for Taskflow API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routers import auth, tasks
from app.models import User, Task, UserRole
from app.auth.security import get_password_hash
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Seed initial data (for demo purposes)
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Check if we need to create default users
        pm_count = db.query(User).filter(User.role == UserRole.PROJECT_MANAGER).count()
        if pm_count == 0:
            # Create default Project Manager
            pm_user = User(
                username="project_manager",
                email="pm@taskflow.com",
                full_name="Project Manager",
                hashed_password=get_password_hash("pm123"),
                role=UserRole.PROJECT_MANAGER
            )
            db.add(pm_user)
            
            # Create default Backend Developer
            dev_user = User(
                username="backend_dev",
                email="dev@taskflow.com",
                full_name="Backend Developer",
                hashed_password=get_password_hash("dev123"),
                role=UserRole.BACKEND_DEVELOPER
            )
            db.add(dev_user)
            
            db.commit()
            print("Default users created successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()
    
    yield
    
    # Shutdown
    print("Taskflow API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Taskflow API",
    description="A comprehensive task management API with role-based access control",
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": True,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": True,
            "status_code": 500
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to Taskflow API",
        "version": settings.api_version,
        "documentation": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": settings.api_version
    }


# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)