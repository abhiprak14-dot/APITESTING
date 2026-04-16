import httpx
from config import settings

async def screenshot_url(url: str) -> bytes:
    """Takes a screenshot of a URL using Browserless API with stealth mode"""
    api_url = f"https://production-sfo.browserless.io/screenshot?token={settings.browserless_api_key}&stealth=true"
    payload = {"url": url, "options": {"fullPage": True, "type": "png"}}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(api_url, json=payload)
        response.raise_for_status()
        return response.content
