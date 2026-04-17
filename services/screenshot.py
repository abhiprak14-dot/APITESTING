import httpx
import re
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

async def post_to_jsfiddle(html: str, css: str = "") -> str:
    proxy_url = f"http://scraperapi:{settings.scraper_api_key}@proxy-server.scraperapi.com:8001"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://jsfiddle.net",
        "Referer": "https://jsfiddle.net/",
        "X-Requested-With": "XMLHttpRequest",
    }

    async with httpx.AsyncClient(
        timeout=60.0,
        follow_redirects=False,
        proxy=proxy_url,
        verify=False,  # ← fix: disable SSL verification for proxy
        headers=headers
    ) as client:
        home = await client.get("https://jsfiddle.net/")
        print(f"Homepage via proxy: {home.status_code}")

        csrf = client.cookies.get("csrftoken", "")
        if not csrf:
            match = re.search(r'csrfmiddlewaretoken.*?value="([^"]+)"', home.text)
            csrf = match.group(1) if match else ""
        print(f"CSRF: {csrf}")

        response = await client.post(
            "https://jsfiddle.net/api/post/library/pure/",
            data={"html": html, "css": css, "wrap": "b", "csrfmiddlewaretoken": csrf},
            headers={**headers, "X-CSRFToken": csrf}
        )
        print(f"POST status via proxy: {response.status_code}")

        if response.status_code not in (200, 301, 302, 303):
            raise ValueError(f"JSFiddle POST failed. Status: {response.status_code}")

        location = response.headers.get("location", "")
        if not location and response.status_code == 200:
            match = re.search(r'"url"\s*:\s*"([^"]+)"', response.text)
            location = match.group(1) if match else ""

        print(f"Location: {location}")
        return location

async def screenshot_html(html: str, css: str = "") -> bytes:
    location = await post_to_jsfiddle(html, css)

    if location.startswith("/"):
        fiddle_url = "https://jsfiddle.net" + location
    else:
        fiddle_url = location

    fiddle_url = fiddle_url.rstrip("/") + "/show"
    print(f"Final URL: {fiddle_url}")
    return await screenshot_url(fiddle_url)
