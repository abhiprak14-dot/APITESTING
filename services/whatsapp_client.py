import httpx
from pydantic import BaseModel
import logging
from ..config import settings
from ..models.custom_api import Template

logger = logging.getLogger(__name__)

class WhatsAppClient:
    def __init__(self):
        self.base_url = f"{settings.whatsapp_graph_url}/{settings.whatsapp_phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.whatsapp_token}",
            "Content-Type": "application/json"
        }

    async def _send_request(self, payload: dict) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.text}")
                raise e
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                raise e

    async def send_text_message(self, to: str, body: str) -> dict:
        """Sends a simple text message via WhatsApp API."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body}
        }
        return await self._send_request(payload)

    async def send_template_message(self, to: str, template: Template) -> dict:
        """Sends a template message via WhatsApp API."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": template.model_dump(exclude_none=True)
        }
        return await self._send_request(payload)

whatsapp_client = WhatsAppClient()
