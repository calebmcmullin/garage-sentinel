from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from tasks.lifespan import lifespan
from starlette.exceptions import HTTPException as StarletteHTTPException
from exceptions.handlers import http_exception_handler
from config import SESSION_SECRET
from routes import (
    home, home_login, home_photos, home_clips, home_account, telemetry, docs,
    file, auth, users, admin
)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

# Include routers:
# API
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(file.router)
app.include_router(telemetry.router)

# Web Pages
app.include_router(home.router)
app.include_router(home_login.router)
app.include_router(home_photos.router)
app.include_router(home_clips.router)
app.include_router(home_account.router)

# Docs
app.include_router(docs.router)