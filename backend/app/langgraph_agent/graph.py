"""
The AIVOA Copilot agent graph.

    START
      |
      v
  classify_intent          <-- decides: log_complaint / edit_complaint /
      |                         document_extraction / general_chat
      v
  extract_and_merge         <-- LLM extracts fields from the new input and
      |                         merges them into the existing form state
      v
  risk_assessment            <-- LLM reasons over the merged form and
      |                         produces severity / next action / CAPA
      v
  compose_reply               <-- LLM writes the natural-language chat reply
      |
      v
     END

Every node reads/writes the shared AgentState TypedDict. The graph is the
same for chat-based "log"/"edit" and for document-extraction; the only
difference is how `user_input` is populated before invoking the graph
(typed text vs. text pulled out of an uploaded PDF/email).
"""
from langgraph.graph import StateGraph, END

from app.langgraph_agent.state import AgentState
from app.langgraph_agent.nodes import (
    classify_intent_node,
    extract_and_merge_node,
    risk_assessment_node,
    compose_reply_node,
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("extract_and_merge", extract_and_merge_node)
    graph.add_node("risk_assessment", risk_assessment_node)
    graph.add_node("compose_reply", compose_reply_node)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "extract_and_merge")
    graph.add_edge("extract_and_merge", "risk_assessment")
    graph.add_edge("risk_assessment", "compose_reply")
    graph.add_edge("compose_reply", END)

    return graph.compile()


# Compiled once at import time and reused across requests.
copilot_agent = build_graph()
