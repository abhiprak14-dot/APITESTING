import httpx
from config import settings

async def screenshot_url(url: str, delay: int = 5) -> bytes:
    """
    Takes a screenshot of any public URL.
    Uses ScreenshotOne on Render, Playwright in production.
    """
    if settings.use_playwright:
        return await _playwright_screenshot(url)
    else:
        return await _screenshotone_screenshot(url, delay)

async def _screenshotone_screenshot(url: str, delay: int = 5) -> bytes:
    """Uses ScreenshotOne API"""
    api_url = "https://api.screenshotone.com/take"
    params = {
        "access_key": settings.screenshot_api_key,
        "url": url,
        "format": "png",
        "viewport_width": 680,
        "viewport_height": 900,
        "full_page": "true",
        "delay": delay
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()
        return response.content

async def _playwright_screenshot(url: str) -> bytes:
    """Uses Playwright - for production with Docker"""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 680, "height": 900})
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(5000)
        screenshot = await page.screenshot(full_page=True)
        await browser.close()
        return screenshot
