from typing import TypedDict, Optional, Dict, Any


class AgentState(TypedDict, total=False):
    """
    Shared state that flows through the LangGraph graph for a single
    turn of the AIVOA Copilot.
    """
    # --- input ---
    user_input: str                 # raw text typed by user, or text extracted from an uploaded doc
    source_channel: str             # "chat" | "document"
    is_new_complaint: bool          # True if there is no existing complaint in this session yet

    # --- routing ---
    intent: str                     # "log_complaint" | "edit_complaint" | "document_extraction" | "general_chat"

    # --- working data (mirrors the DB model fields) ---
    existing_fields: Dict[str, Any]     # current complaint form state before this turn
    updated_fields: Dict[str, Any]      # merged form state after extraction
    existing_risk: Dict[str, Any]       # current risk assessment before this turn
    updated_risk: Dict[str, Any]        # new risk assessment after reasoning

    # --- output ---
    reply: str                      # natural-language message shown back in the copilot chat
    tool_used: str
