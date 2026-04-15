from playwright.async_api import async_playwright

async def screenshot_url(url: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 630})
        await page.goto(url, wait_until="networkidle")
        screenshot = await page.screenshot(full_page=False)
        await browser.close()
        return screenshot
