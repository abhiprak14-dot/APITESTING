from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict

class Profile(BaseModel):
    name: str

class Contact(BaseModel):
    profile: Profile
    wa_id: str

class TextMessage(BaseModel):
    body: str

class MetaData(BaseModel):
    display_phone_number: str
    phone_number_id: str

class Message(BaseModel):
    from_: str = None
    id: str
    timestamp: str
    text: Optional[TextMessage] = None
    type: str
    
    # We use alias to map "from" (Python reserved keyword) to "from_"
    model_config = ConfigDict(populate_by_name=True, alias_generator=lambda field_name: "from" if field_name == "from_" else field_name)

class Value(BaseModel):
    messaging_product: str
    metadata: MetaData
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None
    statuses: Optional[List[Dict[str, Any]]] = None

class Change(BaseModel):
    value: Value
    field: str

class Entry(BaseModel):
    id: str
    changes: List[Change]

class WebhookPayload(BaseModel):
    object: str
    entry: List[Entry]
