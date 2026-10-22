import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

from app.api import academic, admin, auth, verification
from app.core.config import settings
from app.core.body_limit import BodyLimit
from app.db.session import engine

app = FastAPI(title="SPVS API", version="1.0.0", description="Two layers: identity and physical presence. See docs for assurance limits.")
app.add_middleware(BodyLimit)
app.add_middleware(CORSMiddleware, allow_origins=settings().cors_origins.split(","),
                   allow_credentials=False, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and (not length.isdigit() or int(length) > 15_000_000):
        return JSONResponse({"error": {"code": 413, "message": "Request body too large"}}, status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "same-origin"
    return response


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse({"error": {"code": exc.status_code, "message": exc.detail}}, status_code=exc.status_code, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Do not echo passwords, base64 faces or signed evidence in validation responses.
    return JSONResponse({"error": {"code": 422, "message": "Invalid request", "fields": [".".join(map(str, e["loc"])) for e in exc.errors()]}}, status_code=422)


@app.exception_handler(IntegrityError)
async def conflict(request, exc):
    return JSONResponse({"error": {"code": 409, "message": "Conflicting or referenced record"}}, status_code=409)


@app.exception_handler(RuntimeError)
async def unavailable(request, exc):
    logging.getLogger("spvs").error("Service unavailable: %s", type(exc).__name__)
    return JSONResponse({"error": {"code": 503, "message": "Verification service unavailable; check server model configuration"}}, status_code=503)


@app.get("/health", tags=["Operations"])
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@app.get("/ready", tags=["Operations"])
def ready():
    from app.services.vision import get_vision
    health()
    get_vision()
    return {"status": "ready", "face_models": "loaded", "attestation": "not_configured"}


for router in (auth.router, academic.router, admin.router, verification.router):
    app.include_router(router, prefix="/api/v1")
