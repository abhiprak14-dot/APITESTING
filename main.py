import logging
import uuid
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from config import settings
from routers import webhook, messaging

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="WhatsApp Graph API Boilerplate",
    description="A simple FastAPI service to send and receive WhatsApp messages via the Graph API.",
    version="1.0.0"
)

# In-memory report storage
reports = {}

def inject_open_in_browser(html: str, report_url: str) -> str:
    """Injects an Open in Browser button into the HTML"""
    button = f"""
    <a href="{report_url}" target="_blank"
       style="position:fixed; bottom:20px; right:20px;
              background:#25D366; color:white;
              padding:10px 20px; border-radius:20px;
              font-family:Arial; text-decoration:none;
              font-size:14px; z-index:9999;">
       Open in Browser
    </a>
    """
    return html.replace("</body>", f"{button}</body>")

@app.get("/")
async def root():
    return {"status": "ok", "message": "WhatsApp Integration API is running"}

@app.post("/upload-report")
async def upload_report(html_content: str):
    """Store HTML and return a public URL"""
    report_id = str(uuid.uuid4())
    report_url = f"{settings.server_url}/report/{report_id}"
    reports[report_id] = inject_open_in_browser(html_content, report_url)
    return {"report_id": report_id, "url": report_url}

@app.get("/report/{report_id}")
async def get_report(report_id: str):
    """Serve a stored HTML report"""
    if report_id not in reports:
        return HTMLResponse(content="<h1>Report not found</h1>", status_code=404)
    return HTMLResponse(content=reports[report_id])

@app.get("/report")
async def get_static_report():
    """Serve the static morning report for testing"""
    return FileResponse("morning_SINGLE_7AM.html")

app.include_router(webhook.router)
app.include_router(messaging.router)
