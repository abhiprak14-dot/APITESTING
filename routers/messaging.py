import logging
from fastapi import APIRouter, Depends, HTTPException, status
from auth import get_api_key
from models.custom_api import SendTextRequest, SendTemplateRequest
from services.whatsapp_client import whatsapp_client

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

@router.post("/send-report")
async def send_report(
    to_phone_number: str,
    page_url: str,
    template_name: str,
    api_key: str = Depends(get_api_key)
):
    """
    Screenshots a URL and sends it as a WhatsApp template message
    with an image header and a URL button.
    """
    from services.screenshot import screenshot_url
    
    # 1. Screenshot the page
    image_bytes = await screenshot_url(page_url)
    
    # 2. Upload to Meta
    media_id = await whatsapp_client.upload_media(image_bytes)
    
    # 3. Send WhatsApp message
    response = await whatsapp_client.send_template_with_image(
        to=to_phone_number,
        media_id=media_id,
        template_name=template_name,
        page_url=page_url
    )
    return {"status": "success", "data": response}

@router.get("/test-screenshot")
async def test_screenshot(
    page_url: str,
    api_key: str = Depends(get_api_key)
):
    """Test endpoint to verify Playwright screenshot works on Render"""
    from services.screenshot import screenshot_url
    from fastapi.responses import Response
    
    image_bytes = await screenshot_url(page_url)
    return Response(content=image_bytes, media_type="image/png")

@router.get("/test-jsfiddle-screenshot")
async def test_jsfiddle_screenshot(
    api_key: str = Depends(get_api_key)
):
    """Test JSFiddle POST API screenshot"""
    from services.screenshot import screenshot_html
    from fastapi.responses import Response
    import os
    
    with open("morning_SINGLE_7AM.html", "r") as f:
        html_content = f.read()
    
    image_bytes = await screenshot_html(html_content)
    return Response(content=image_bytes, media_type="image/png")
