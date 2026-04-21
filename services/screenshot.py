import httpx
import io
import uuid
from urllib.parse import unquote_plus, quote
from PIL import Image
from config import settings

async def screenshot_url(url: str, delay: int = 10) -> bytes:
    url = unquote_plus(url)
    if settings.use_playwright:
        return await _playwright_screenshot(url, delay)
    else:
        return await _screenshotone_screenshot(url, delay)

async def host_screenshot(image_bytes: bytes) -> str:
    from main import screenshots
    screenshot_id = str(uuid.uuid4())
    screenshots[screenshot_id] = image_bytes
    return f"{settings.server_url}/screenshots/{screenshot_id}"

async def _screenshotone_screenshot(url: str, delay: int = 10) -> bytes:
    api_url = "https://api.screenshotone.com/take"
    # Pass url as encoded param to avoid issues
    encoded_url = quote(url, safe='')
    full_url = (
        f"{api_url}"
        f"?access_key={settings.screenshot_api_key}"
        f"&url={encoded_url}"
        f"&format=png"
        f"&viewport_width=700"
        f"&viewport_height=700"
        f"&full_page=false"
        f"&delay={delay}"
    )
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(full_url)
        response.raise_for_status()
        return response.content

async def _playwright_screenshot(url: str, delay_ms: int = 10000) -> bytes:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 700, "height": 700})
        await page.goto(url, wait_until="networkidle")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(delay_ms)
        screenshot = await page.screenshot(full_page=False)
        await browser.close()
        return screenshot
