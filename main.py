import logging
from fastapi import FastAPI
from config import settings
from routers import webhook, messaging

# Configure root logger
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="WhatsApp Graph API Boilerplate",
    description="A simple FastAPI service to send and receive WhatsApp messages via the Graph API.",
    version="1.0.0"
)

# Root endpoint for health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "WhatsApp Integration API is running"}

# Include application routers
app.include_router(webhook.router)
app.include_router(messaging.router)
