import httpx
from config import settings

def normalize_jsfiddle_url(url: str) -> str:
    url = url.rstrip("/")
    if "jsfiddle.net" in url and not url.endswith("/show"):
        url = url + "/show"
    return url

async def screenshot_url(url: str) -> bytes:
    url = normalize_jsfiddle_url(url)
    print(f"Screenshotting URL: {url}")

    api_url = "https://api.screenshotone.com/take"
    params = {
        "access_key": settings.screenshot_api_key,
        "url": url,
        "format": "png",
        "viewport_width": 680,
        "viewport_height": 900,
        "full_page": "true",
        "delay": 3,
        "block_cookie_banners": "true",
        "block_ads": "true",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()
        return response.content

async def screenshot_html(html: str, css: str = "") -> bytes:
    """Posts HTML to JSFiddle API mimicking a real browser request."""

    # Full browser-like headers to bypass JSFiddle's 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://jsfiddle.net",
        "Referer": "https://jsfiddle.net/",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Connection": "keep-alive",
    }

    # Use a persistent session to carry cookies (like a real browser)
    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=False,
        headers=headers
    ) as client:
        # Step 1: Visit JSFiddle homepage first to get session cookies
        await client.get("https://jsfiddle.net/")
        print("Got JSFiddle session cookies")

        # Step 2: POST the HTML with cookies in place
        fiddle_response = await client.post(
            "https://jsfiddle.net/api/post/library/pure/",
            data={"html": html, "css": css, "wrap": "b"}
        )

    print(f"JSFiddle POST status: {fiddle_response.status_code}")
    print(f"JSFiddle headers: {dict(fiddle_response.headers)}")

    if fiddle_response.status_code not in (301, 302, 303):
        raise ValueError(
            f"JSFiddle did not redirect. Status: {fiddle_response.status_code}, "
            f"Body: {fiddle_response.text[:200]}"
        )

    # Step 3: Extract redirect location
    location = fiddle_response.headers.get("location", "")
    print(f"JSFiddle redirect location: {location}")

    if location.startswith("/"):
        fiddle_url = "https://jsfiddle.net" + location
    else:
        fiddle_url = location

    fiddle_url = fiddle_url.rstrip("/") + "/show"
    print(f"Final JSFiddle URL: {fiddle_url}")

    return await screenshot_url(fiddle_url)
