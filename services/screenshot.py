import httpx
import io
import uuid
from PIL import Image
from config import settings

async def screenshot_url(url: str, delay: int = 10) -> bytes:
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
        image_bytes = response.content

    # Crop to top portion at WhatsApp ratio
    img = Image.open(io.BytesIO(image_bytes))
    width = img.size[0]
    whatsapp_height = int(width / 1.91)
    img_cropped = img.crop((0, 0, width, whatsapp_height))
    output = io.BytesIO()
    img_cropped.save(output, format="PNG")
    return output.getvalue()

async def _playwright_screenshot(url: str, delay_ms: int = 10000) -> bytes:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 680, "height": 900})
        await page.goto(url, wait_until="networkidle")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(delay_ms)

        report_box = await page.evaluate('''() => {
            const el = document.querySelector(".email-frame") ||
                       document.querySelector(".stage") ||
                       document.body;
            const rect = el.getBoundingClientRect();
            return {x: rect.x, y: rect.y,
                    width: rect.width, height: rect.height};
        }''')

        # Crop to top portion at WhatsApp ratio
        width = report_box["width"]
        whatsapp_height = width / 1.91

        screenshot = await page.screenshot(
            full_page=False,
            clip={
                "x": report_box["x"],
                "y": report_box["y"],
                "width": width,
                "height": whatsapp_height
            }
        )
        await browser.close()
        return screenshot
