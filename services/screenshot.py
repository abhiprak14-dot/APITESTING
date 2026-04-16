import httpx
from config import settings

async def screenshot_url(url: str) -> bytes:
    """Takes a screenshot of a URL using ScreenshotOne API"""
    api_url = "https://api.screenshotone.com/take"
    params = {
        "access_key": settings.screenshot_api_key,
        "url": url,
        "format": "png",
        "viewport_width": 1200,
        "viewport_height": 630,
        "full_page": "false"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()
        return response.content
