import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from auth import get_api_key
from models.custom_api import SendTextRequest, SendTemplateRequest
from services.whatsapp_client import whatsapp_client
from services.screenshot import screenshot_url, host_screenshot

router = APIRouter(prefix="/api/messages", tags=["Messaging"])
logger = logging.getLogger(__name__)

@router.post("/send-text")
async def send_custom_text(
    request: SendTextRequest,
    api_key: str = Depends(get_api_key)
):
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
    """Screenshots a URL and sends via Meta direct API."""
    image_bytes = await screenshot_url(page_url)
    media_id = await whatsapp_client.upload_media(image_bytes)
    response = await whatsapp_client.send_template_with_image(
        to=to_phone_number,
        media_id=media_id,
        template_name=template_name,
        page_url=page_url
    )
    return {"status": "success", "data": response}

@router.post("/send-report-relay")
async def send_report_relay(
    to_phone_number: str,
    report_url: str,
    user_name: str,
    api_key: str = Depends(get_api_key)
):
    """
    1. Screenshots the report URL
    2. Hosts screenshot on our Render server
    3. Sends via relay API with:
       - image hosted on Render (no expiry)
       - report link sent as separate text message (bypasses link shortener)
    """
    # 1. Screenshot the report
    image_bytes = await screenshot_url(report_url)

    # 2. Host screenshot on Render
    image_url = await host_screenshot(image_bytes)

    # 3. Send template with image
    response = await whatsapp_client.send_report_via_relay(
        to=to_phone_number,
        image_url=image_url,
        user_name=user_name,
        report_url=report_url
    )

    # 4. Send report URL as separate text message (bypasses link shortener)
    await whatsapp_client.send_text_message(
        to=to_phone_number,
        body=f"View your full report here:\n{report_url}"
    )

    return {
        "status": "success",
        "image_url": image_url,
        "data": response
    }

@router.get("/test-screenshot")
async def test_screenshot(
    page_url: str,
    api_key: str = Depends(get_api_key)
):
    """Test screenshot of any URL"""
    image_bytes = await screenshot_url(page_url)
    return Response(content=image_bytes, media_type="image/png")
