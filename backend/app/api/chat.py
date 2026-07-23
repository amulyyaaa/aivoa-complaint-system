from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.langgraph_agent.graph import copilot_agent
from app.langgraph_agent.state import AgentState

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _complaint_to_fields(c: models.Complaint) -> dict:
    return {
        "customer_name": c.customer_name,
        "product_name": c.product_name,
        "product_strength": c.product_strength,
        "batch_number": c.batch_number,
        "manufacturing_date": c.manufacturing_date,
        "expiry_date": c.expiry_date,
        "affected_quantity": c.affected_quantity,
        "complaint_type": c.complaint_type,
        "complaint_description": c.complaint_description,
        "date_reported": c.date_reported,
    }


def _complaint_to_risk(c: models.Complaint) -> dict:
    return {
        "severity": c.severity,
        "risk_category": c.risk_category,
        "recommended_next_action": c.recommended_next_action,
        "recommended_capa": c.recommended_capa,
        "ai_reasoning_summary": c.ai_reasoning_summary,
    }


def run_copilot_turn(
    db: Session,
    user_input: str,
    complaint_id: str | None,
    source_channel: str = "chat",
) -> tuple[models.Complaint, str, str]:
    """
    Shared helper used by both the chat endpoint and the document-upload
    endpoint to invoke the LangGraph agent and persist the result.
    Returns (complaint_row, assistant_reply, tool_used).
    """
    complaint = db.query(models.Complaint).get(complaint_id) if complaint_id else None
    is_new = complaint is None

    initial_state: AgentState = {
        "user_input": user_input,
        "source_channel": source_channel,
        "is_new_complaint": is_new,
        "existing_fields": _complaint_to_fields(complaint) if complaint else {},
        "existing_risk": _complaint_to_risk(complaint) if complaint else {},
    }

    result_state = copilot_agent.invoke(initial_state)

    if complaint is None:
        complaint = models.Complaint(source_channel=source_channel)
        db.add(complaint)

    fields = result_state.get("updated_fields", {})
    risk = result_state.get("updated_risk", {})
    for k, v in fields.items():
        setattr(complaint, k, v)
    for k, v in risk.items():
        setattr(complaint, k, v)

    db.commit()
    db.refresh(complaint)

    db.add(models.ChatMessage(complaint_id=complaint.id, role="user", content=user_input))
    db.add(models.ChatMessage(
        complaint_id=complaint.id, role="assistant",
        content=result_state["reply"], tool_used=result_state["tool_used"],
    ))
    db.commit()

    return complaint, result_state["reply"], result_state["tool_used"]


@router.post("", response_model=schemas.ChatResponse)
def chat(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not req.message or not req.message.strip():
        raise HTTPException(400, "message cannot be empty")

    complaint, reply, tool_used = run_copilot_turn(
        db, user_input=req.message, complaint_id=req.complaint_id, source_channel="chat"
    )
    return schemas.ChatResponse(reply=reply, tool_used=tool_used, complaint=complaint)
