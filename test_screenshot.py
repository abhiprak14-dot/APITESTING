import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import io

URL = "https://userapi.neolook.ai/api/v1/reports/morning-account?user_token=GlqPBe3Tpt9YjKET96Kq_EFCnVT16KZBqnsWmQjWKaU&account_id=act_2138449746591192&email_to=sushan%40neolook.ai%2C%20janesh.mishra%40neolook.ai%2C%20prakash%40neolook.ai&email_subject=Morning%20Account%20Report%20-%20Testing"

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(10000)

        # Get exact report element
        report_box = await page.evaluate('''() => {
            const el = document.querySelector(".email-frame") || 
                       document.querySelector(".stage") ||
                       document.body;
            const rect = el.getBoundingClientRect();
            return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
        }''')

        # Capture FULL report - no cropping
        screenshot_bytes = await page.screenshot(
            full_page=True,
            clip={
                "x": report_box["x"],
                "y": report_box["y"],
                "width": report_box["width"],
                "height": report_box["height"]
            }
        )
        await browser.close()

        img = Image.open(io.BytesIO(screenshot_bytes))
        img.save("api_report.png")
        print(f"Image size: {img.size}")
        print("Done!")

asyncio.run(test())
