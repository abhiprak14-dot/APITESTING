import httpx

URL_SHORTENER_BASE = "https://url-shortener-0ziy.onrender.com"

def shorten_url(long_url: str) -> str:
    try:
        response = httpx.post(
            f"{URL_SHORTENER_BASE}/shorten",
            json={"original_url": long_url},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()["short_url"]
    except Exception as e:
        print(f"URL shortening failed: {e}")
        return long_url  # fallback to original if shortener is down
