import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.database import get_db
from app import schemas
from app.config import settings
from app.api.chat import run_copilot_turn

router = APIRouter(prefix="/api/upload", tags=["upload"])


def _extract_text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    # Treat everything else (.txt/.eml) as plain text
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


@router.post("/document", response_model=schemas.ChatResponse)
async def upload_document(
    file: UploadFile = File(...),
    complaint_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """
    Document extraction tool: accepts a PDF or plain-text/email file
    containing a customer complaint, extracts the text, and runs it
    through the same LangGraph agent used for chat -- populating both
    the Log Customer Complaint form and the AI Copilot Risk Assessment.
    """
    allowed = (".pdf", ".txt", ".eml")
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(400, f"Unsupported file type. Allowed: {allowed}")

    tmp_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    try:
        text = _extract_text(tmp_path)
        if not text.strip():
            raise HTTPException(422, "Could not extract any text from the uploaded document")

        complaint, reply, tool_used = run_copilot_turn(
            db, user_input=text, complaint_id=complaint_id, source_channel="document"
        )
        return schemas.ChatResponse(reply=reply, tool_used=tool_used, complaint=complaint)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
