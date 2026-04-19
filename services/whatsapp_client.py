import httpx
from pydantic import BaseModel
import logging
from config import settings
from models.custom_api import Template
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
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body}
        }
        return await self._send_request(payload)

    async def send_template_message(self, to: str, template: Template) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": template.model_dump(exclude_none=True)
        }
        return await self._send_request(payload)

    async def upload_media(self, image_bytes: bytes) -> str:
        url = f"{settings.whatsapp_graph_url}/{settings.whatsapp_phone_number_id}/media"
        files = {
            "file": ("screenshot.png", image_bytes, "image/png"),
            "type": (None, "image/png"),
            "messaging_product": (None, "whatsapp")
        }
        headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, headers=headers)
            response.raise_for_status()
            return response.json()["id"]

    async def send_template_with_image(self, to: str, media_id: str, template_name: str, page_url: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"},
                "components": [
                    {
                        "type": "header",
                        "parameters": [{"type": "image", "image": {"id": media_id}}]
                    },
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": page_url}]
                    }
                ]
            }
        }
        return await self._send_request(payload)

    async def send_image_with_caption(self, to: str, media_id: str, caption: str) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {"id": media_id, "caption": caption}
        }
        return await self._send_request(payload)

    async def send_report_via_relay(
        self,
        to: str,
        image_url: str,
        user_name: str,
        report_url: str
    ) -> dict:
        """Send report via messaginghub relay API"""
        url = f"{settings.relay_api_url}/messages"
        headers = {
            "x-api-key": settings.relay_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": settings.relay_template_name,
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "image",
                                "image": {"link": image_url}
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": user_name
                            }
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [
                            {
                                "type": "text",
                                "text": report_url
                            }
                        ]
                    }
                ]
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

whatsapp_client = WhatsAppClient()
