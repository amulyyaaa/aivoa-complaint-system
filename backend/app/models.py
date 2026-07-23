import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Complaint(Base):
    """
    Represents a single customer complaint record.
    This mirrors the fields shown in the 'Log Customer Complaint' form.
    """
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=True)

    # --- Complaint / product details ---
    customer_name = Column(String(255))
    product_name = Column(String(255))
    product_strength = Column(String(100))          # e.g. "500 mg" or "IP/BP grade"
    batch_number = Column(String(100))
    manufacturing_date = Column(String(50))
    expiry_date = Column(String(50))
    affected_quantity = Column(String(100))          # kept as string: "48 capsules", "50 kg, 2 HDPE drums"
    complaint_type = Column(String(150))              # e.g. "Discoloration", "Contamination"
    complaint_description = Column(Text)
    date_reported = Column(String(50))
    source_channel = Column(String(50))               # chat / document / email

    # --- AI Copilot Risk Assessment ---
    severity = Column(String(50))                     # Minor / Major / Critical
    risk_category = Column(String(150))
    recommended_next_action = Column(Text)
    recommended_capa = Column(Text)
    ai_reasoning_summary = Column(Text)

    status = Column(String(50), default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="complaint")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    """
    Stores the AIVOA Copilot conversation, linked to the complaint it
    is actively building/editing so the AI has memory of prior turns.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(String(36), ForeignKey("complaints.id"), nullable=True)
    role = Column(String(20))          # user / assistant
    content = Column(Text)
    tool_used = Column(String(50), nullable=True)   # log_complaint / edit_complaint / document_extraction
    created_at = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="messages")
