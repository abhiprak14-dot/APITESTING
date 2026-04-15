import logging
from fastapi import APIRouter, Request, Query, HTTPException, status
from ..config import settings
from ..models.whatsapp import WebhookPayload

router = APIRouter(prefix="/webhook", tags=["Webhook"])

logger = logging.getLogger(__name__)

@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Handles Meta's Webhook verification.
    Required when setting up your webhook URL in the Meta App Dashboard.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.webhook_verify_token:
        logger.info("Webhook verified successfully!")
        return int(hub_challenge)
    
    logger.warning("Failed webhook verification")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")

@router.post("")
async def receive_webhook(payload: WebhookPayload):
    """
    Receives incoming events (messages, status updates) from the WhatsApp API.
    """
    logger.info(f"Received webhook payload: {payload.model_dump_json(indent=2)}")
    
    # Example logic to extract a text message
    for entry in payload.entry:
        for change in entry.changes:
            value = change.value
            if value.messages:
                for message in value.messages:
                    if message.type == "text" and message.text:
                        pass # Process the message.text.body here
                        sender = message.from_
                        logger.info(f"Received text message from {sender}: {message.text.body}")
            
            if value.statuses:
                for msg_status in value.statuses:
                    pass # Process message read/delivered receipts here
                    logger.info(f"Message {msg_status.get('id')} status changed to {msg_status.get('status')}")

    # Return 200 OK immediately to Meta to acknowledge receipt
    return {"status": "ok"}
