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
    1. Fetches HTML from report URL
    2. Stores it on Render at /report/{id}
    3. Screenshots the Render URL
    4. Hosts screenshot on Render at /screenshots/{id}
    5. Sends via relay API with Render URLs (no expiry, no link shortener)
    """
    import uuid
    from main import reports
    from config import settings

    # 1. Fetch HTML from report URL
    async with httpx.AsyncClient(timeout=30.0) as client:
        html_response = await client.get(report_url)
        html_response.raise_for_status()
        html_content = html_response.text

    # 2. Store HTML on Render
    report_id = str(uuid.uuid4())
    hosted_report_url = f"{settings.server_url}/report/{report_id}"
    reports[report_id] = html_content

    # 3. Screenshot the Render URL
    image_bytes = await screenshot_url(hosted_report_url)

    # 4. Host screenshot on Render
    image_url = await host_screenshot(image_bytes)

    # 5. Send via relay API with Render URLs
    response = await whatsapp_client.send_report_via_relay(
        to=to_phone_number,
        image_url=image_url,
        user_name=user_name,
        report_url=hosted_report_url  # Render URL - never expires
    )
    return {
        "status": "success",
        "hosted_report_url": hosted_report_url,
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
