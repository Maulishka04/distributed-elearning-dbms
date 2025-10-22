"""
Main FastAPI application for E-Learning Platform
Includes API versioning, JWT authentication, rate limiting, and error handling.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from api.routers import users, courses, enrollments, payments, auth
from api.utils.rate_limit import RateLimitMiddleware

app = FastAPI(
    title="Global E-Learning Platform API",
    description="REST API for users, courses, enrollments, and payments.",
    version="v1"
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
app.include_router(enrollments.router, prefix="/api/v1/enrollments", tags=["enrollments"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.get("/api/v1/health", tags=["system"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Sample root endpoint
@app.get("/", tags=["system"])
async def root():
    """Root endpoint for API documentation."""
    return {"message": "Welcome to the Global E-Learning Platform API"}
