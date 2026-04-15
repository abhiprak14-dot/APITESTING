from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class SendTextRequest(BaseModel):
    to_phone_number: str = Field(..., description="The recipient's phone number with country code")
    message_body: str = Field(..., description="The text message content")

class Language(BaseModel):
    code: str

class TemplateComponent(BaseModel):
    type: str
    parameters: List[Dict[str, Any]]

class Template(BaseModel):
    name: str
    language: Language
    components: Optional[List[TemplateComponent]] = None

class SendTemplateRequest(BaseModel):
    to_phone_number: str = Field(..., description="The recipient's phone number with country code")
    template: Template = Field(..., description="The template object details")
