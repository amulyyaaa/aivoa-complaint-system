from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ComplaintForm(BaseModel):
    """Left-hand 'Log Customer Complaint' form fields."""
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    affected_quantity: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_description: Optional[str] = None
    date_reported: Optional[str] = None
    source_channel: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RiskAssessment(BaseModel):
    """Right-hand 'AI Copilot Risk Assessment' fields."""
    severity: Optional[str] = None
    risk_category: Optional[str] = None
    recommended_next_action: Optional[str] = None
    recommended_capa: Optional[str] = None
    ai_reasoning_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ComplaintOut(ComplaintForm, RiskAssessment):
    id: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str
    complaint_id: Optional[str] = None  # None => start a new complaint


class ChatResponse(BaseModel):
    reply: str
    tool_used: str
    complaint: ComplaintOut


class ChatMessageOut(BaseModel):
    role: str
    content: str
    tool_used: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
