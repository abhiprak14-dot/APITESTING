import httpx
import io
import uuid
from PIL import Image
from config import settings

async def screenshot_url(url: str, delay_ms: int = 10000) -> bytes:
    """
    Takes a full report screenshot.
    Uses Playwright in production, ScreenshotOne on Render.
    """
    if settings.use_playwright:
        return await _playwright_screenshot(url, delay_ms)
    else:
        return await _screenshotone_screenshot(url)

async def host_screenshot(image_bytes: bytes) -> str:
    """
    Store screenshot on our own server and return public URL.
    No third party hosting needed.
    """
    from main import screenshots
    screenshot_id = str(uuid.uuid4())
    screenshots[screenshot_id] = image_bytes
    return f"{settings.server_url}/screenshots/{screenshot_id}"

async def _screenshotone_screenshot(url: str, delay: int = 10) -> bytes:
    """Uses ScreenshotOne API — for Render/testing"""
    api_url = "https://api.screenshotone.com/take"
    params = {
        "access_key": settings.screenshot_api_key,
        "url": url,
        "format": "png",
        "viewport_width": 1400,
        "viewport_height": 900,
        "full_page": "true",
        "delay": delay
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()
        return response.content

async def _playwright_screenshot(url: str, delay_ms: int = 10000) -> bytes:
    """
    Uses Playwright — for production with Docker.
    Crops black borders by finding exact report element.
    """
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(delay_ms)

        # Find exact report element to remove black borders
        report_box = await page.evaluate('''() => {
            const el = document.querySelector(".email-frame") ||
                       document.querySelector(".stage") ||
                       document.body;
            const rect = el.getBoundingClientRect();
            return {
                x: rect.x, y: rect.y,
                width: rect.width, height: rect.height
            };
        }''')

        # Capture full report with no black borders
        screenshot = await page.screenshot(
            full_page=True,
            clip={
                "x": report_box["x"],
                "y": report_box["y"],
                "width": report_box["width"],
                "height": report_box["height"]
            }
        )
        await browser.close()
        return screenshot
