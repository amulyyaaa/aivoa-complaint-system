import json
from datetime import date

from app.langgraph_agent.state import AgentState
from app.langgraph_agent.llm_client import chat_completion, chat_completion_json
from app.langgraph_agent import prompts


def classify_intent_node(state: AgentState) -> AgentState:
    # Document extraction is decided upstream (upload endpoint sets it directly),
    # so this node only needs to distinguish log vs edit vs general chat.
    if state.get("source_channel") == "document":
        state["intent"] = "document_extraction"
        return state

    if state.get("is_new_complaint", True):
        state["intent"] = "log_complaint"
        return state

    raw = chat_completion(prompts.INTENT_SYSTEM_PROMPT, state["user_input"]).strip().lower()
    if "edit" in raw:
        state["intent"] = "edit_complaint"
    elif "log" in raw:
        state["intent"] = "log_complaint"
    else:
        state["intent"] = "general_chat"
    return state


def extract_and_merge_node(state: AgentState) -> AgentState:
    if state["intent"] == "general_chat":
        state["updated_fields"] = state.get("existing_fields", {})
        return state

    existing = state.get("existing_fields", {}) or {}
    user_prompt = (
        f"PREVIOUS FORM STATE (JSON):\n{json.dumps(existing)}\n\n"
        f"NEW INPUT FROM USER:\n{state['user_input']}\n\n"
        f"Today's date is {date.today().isoformat()}.\n"
        f"Return the merged/updated form JSON now."
    )
    extracted = chat_completion_json(prompts.EXTRACTION_SYSTEM_PROMPT, user_prompt)

    # Defensive merge: never let a None from the model wipe an existing value
    # unless the model is clearly asked to overwrite (handled in prompt already).
    merged = dict(existing)
    for k in prompts.FORM_FIELDS:
        v = extracted.get(k)
        if v is not None and str(v).strip() != "":
            merged[k] = v
    state["updated_fields"] = merged
    return state


def risk_assessment_node(state: AgentState) -> AgentState:
    if state["intent"] == "general_chat":
        state["updated_risk"] = state.get("existing_risk", {})
        return state

    fields = state["updated_fields"]
    user_prompt = f"CURRENT COMPLAINT DETAILS (JSON):\n{json.dumps(fields)}\n\nAssess the risk now."
    risk = chat_completion_json(prompts.RISK_SYSTEM_PROMPT, user_prompt)
    state["updated_risk"] = {k: risk.get(k) for k in prompts.RISK_FIELDS}
    return state


def compose_reply_node(state: AgentState) -> AgentState:
    intent = state["intent"]
    state["tool_used"] = intent

    if intent == "general_chat":
        reply = chat_completion(
            "You are AIVOA Copilot, a helpful QMS assistant for pharmaceutical customer complaints. "
            "Answer briefly and helpfully.",
            state["user_input"],
        )
        state["reply"] = reply
        return state

    context = (
        f"INTENT: {intent}\n"
        f"UPDATED FORM FIELDS: {json.dumps(state['updated_fields'])}\n"
        f"UPDATED RISK ASSESSMENT: {json.dumps(state['updated_risk'])}\n"
        f"USER'S LATEST MESSAGE: {state['user_input']}"
    )
    reply = chat_completion(prompts.REPLY_SYSTEM_PROMPT, context)
    state["reply"] = reply
    return state
