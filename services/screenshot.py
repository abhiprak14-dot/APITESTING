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

    # Auto crop black borders from top using PIL
    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size

    # Find first non-black row from top
    top_crop = 0
    for y in range(height):
        row_pixels = [img.getpixel((x, y)) for x in range(0, width, 10)]
        avg_brightness = sum(sum(p[:3]) for p in row_pixels) / (len(row_pixels) * 3)
        if avg_brightness > 20:
            top_crop = y
            break

    # Crop from first non-black row
    img_cropped = img.crop((0, top_crop, width, height))
    output = io.BytesIO()
    img_cropped.save(output, format="PNG")
    return output.getvalue()

async def _playwright_screenshot(url: str, delay_ms: int = 10000) -> bytes:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(delay_ms)

        report_box = await page.evaluate('''() => {
            const el = document.querySelector(".email-frame") ||
                       document.querySelector(".stage") ||
                       document.body;
            const rect = el.getBoundingClientRect();
            return {x: rect.x, y: rect.y,
                    width: rect.width, height: rect.height};
        }''')

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
