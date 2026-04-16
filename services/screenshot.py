import httpx
from config import settings

async def screenshot_url(url: str) -> bytes:
    api_url = "https://api.screenshotone.com/take"
    params = {
        "access_key": settings.screenshot_api_key,
        "url": url,
        "format": "png",
        "viewport_width": 680,
        "viewport_height": 900,
        "full_page": "true",
        "delay": 2,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()
        return response.content

async def screenshot_html(html: str, css: str = "") -> bytes:
    """Posts HTML to JSFiddle API and screenshots the result"""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        fiddle_response = await client.post(
            "https://jsfiddle.net/api/post/library/pure/",
            data={"html": html, "css": css, "wrap": "b"}
        )
        # Get the final URL after redirect e.g. https://jsfiddle.net/abc123/
        fiddle_url = str(fiddle_response.url)
        # Remove trailing slash and add /show
        fiddle_url = fiddle_url.rstrip("/") + "/show"
    
    print(f"JSFiddle URL: {fiddle_url}")
    return await screenshot_url(fiddle_url)
