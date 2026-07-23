from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).get(complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    return complaint


@router.get("", response_model=list[schemas.ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()


@router.get("/{complaint_id}/messages", response_model=list[schemas.ChatMessageOut])
def get_messages(complaint_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.complaint_id == complaint_id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )
