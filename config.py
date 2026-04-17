from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # WhatsApp API Credentials
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    webhook_verify_token: str = "my_secure_verify_token"
    app_secret: str = ""
    
    # Base URL for WhatsApp Graph API
    whatsapp_graph_url: str = "https://graph.facebook.com/v19.0"

    # Custom API Security
    api_key: str = "change_me_to_a_secure_token"

    # Application settings
    log_level: str = "INFO"

    # Screenshot APIs
    screenshot_api_key: str = ""
    browserless_api_key: str = ""

    # Toggle between ScreenshotOne and Playwright
    # False = ScreenshotOne (Render/testing)
    # True = Playwright (production/Docker)
    use_playwright: bool = False

    # Server URL for report hosting
    server_url: str = "https://test123-h6ew.onrender.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
