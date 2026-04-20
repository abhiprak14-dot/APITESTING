from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # WhatsApp API Credentials (Meta direct)
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    webhook_verify_token: str = "my_secure_verify_token"
    app_secret: str = ""
    whatsapp_graph_url: str = "https://graph.facebook.com/v19.0"

    # Custom API Security
    api_key: str = "change_me_to_a_secure_token"

    # Application settings
    log_level: str = "INFO"

    # Screenshot APIs
    screenshot_api_key: str = ""
    browserless_api_key: str = ""

    # Toggle Playwright vs ScreenshotOne
    use_playwright: bool = False

    # Server URL for hosting screenshots and reports
    server_url: str = "https://test123-h6ew.onrender.com"

    # Relay API settings (messaginghub)
    relay_api_url: str = "https://messaginghub.solutions/relaybridge/api/v1/meta/694a3e0324a85a1a6121b9a4"
    relay_api_key: str = "8722c1e72ef544f29392b1916a2863c4"
    relay_template_name: str = "report_new"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
