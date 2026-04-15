import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ..auth import get_api_key
from ..models.custom_api import SendTextRequest, SendTemplateRequest
from ..services.whatsapp_client import whatsapp_client

router = APIRouter(prefix="/api/messages", tags=["Messaging"])
logger = logging.getLogger(__name__)

@router.post("/send-text")
async def send_custom_text(
    request: SendTextRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Sends a text message to a WhatsApp user.
    Requires a valid X-API-Key header.
    """
    try:
        response = await whatsapp_client.send_text_message(
            to=request.to_phone_number,
            body=request.message_body
        )
        return {"status": "success", "data": response}
    except Exception as e:
        logger.error(f"Failed to send text message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message via WhatsApp API"
        )

@router.post("/send-template")
async def send_custom_template(
    request: SendTemplateRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Sends a template message to a WhatsApp user.
    Requires a valid X-API-Key header.
    """
    try:
        response = await whatsapp_client.send_template_message(
            to=request.to_phone_number,
            template=request.template
        )
        return {"status": "success", "data": response}
    except Exception as e:
        logger.error(f"Failed to send template message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message via WhatsApp API"
        )
