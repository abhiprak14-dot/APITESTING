import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from auth import get_api_key
from models.custom_api import SendTextRequest, SendTemplateRequest
from services.whatsapp_client import whatsapp_client
from services.screenshot import screenshot_url

router = APIRouter(prefix="/api/messages", tags=["Messaging"])
logger = logging.getLogger(__name__)

@router.post("/send-text")
async def send_custom_text(
    request: SendTextRequest,
    api_key: str = Depends(get_api_key)
):
    """Sends a text message to a WhatsApp user."""
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
    """Sends a template message to a WhatsApp user."""
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
    """Screenshots a URL and sends it as a WhatsApp template message."""
    image_bytes = await screenshot_url(page_url)
    media_id = await whatsapp_client.upload_media(image_bytes)
    response = await whatsapp_client.send_template_with_image(
        to=to_phone_number,
        media_id=media_id,
        template_name=template_name,
        page_url=page_url
    )
    return {"status": "success", "data": response}

@router.post("/send-html-report")
async def send_html_report(
    to_phone_number: str,
    template_name: str,
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    Accepts an HTML file, hosts it, screenshots it,
    and sends via WhatsApp with image + link.
    Works for any HTML — dashboards, maps, reports.
    """
    # 1. Read HTML content
    html_content = (await file.read()).decode("utf-8")

    # 2. Upload to our server and get public URL
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:10000/upload-report",
            params={"html_content": html_content}
        )
        report_data = response.json()
        report_url = report_data["url"]

    # 3. Screenshot the public URL
    image_bytes = await screenshot_url(report_url)

    # 4. Upload image to Meta
    media_id = await whatsapp_client.upload_media(image_bytes)

    # 5. Send WhatsApp message with image + link
    response = await whatsapp_client.send_template_with_image(
        to=to_phone_number,
        media_id=media_id,
        template_name=template_name,
        page_url=report_url
    )
    return {
        "status": "success",
        "report_url": report_url,
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
