import React, { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendUserMessage, sendUserDocument } from "../store/chatSlice";
import RiskAssessment from "./RiskAssessment";
import "./CopilotChat.css";

const TOOL_LABEL = {
  log_complaint: "Log Complaint Tool",
  edit_complaint: "Edit Complaint Tool",
  document_extraction: "Document Extraction Tool",
  general_chat: "Copilot",
};

export default function CopilotChat() {
  const dispatch = useDispatch();
  const messages = useSelector((s) => s.chat.messages);
  const isThinking = useSelector((s) => s.chat.isThinking);
  const [draft, setDraft] = useState("");
  const listRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  const handleSend = () => {
    const text = draft.trim();
    if (!text || isThinking) return;
    dispatch(sendUserMessage(text));
    setDraft("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    dispatch(sendUserDocument({ file, fileName: file.name }));
    e.target.value = "";
  };

  return (
    <div className="cc-panel">
      <div className="cc-header">
        <div className="cc-avatar" aria-hidden="true">AI</div>
        <div>
          <h2 className="cc-title">AIVOA Copilot</h2>
          <p className="cc-subtitle">Log, edit, or extract complaints in natural language</p>
        </div>
      </div>

      <RiskAssessment />

      <div className="cc-messages" ref={listRef}>
        {messages.map((m) => (
          <div key={m.id} className={`cc-msg cc-msg-${m.role}`}>
            {m.role === "assistant" && m.toolUsed && (
              <span className={`cc-tool-tag ${m.isError ? "cc-tool-tag-error" : ""}`}>
                {TOOL_LABEL[m.toolUsed] || "Copilot"}
              </span>
            )}
            <div className={`cc-bubble ${m.isError ? "cc-bubble-error" : ""}`}>{m.content}</div>
          </div>
        ))}
        {isThinking && (
          <div className="cc-msg cc-msg-assistant">
            <div className="cc-bubble cc-thinking">
              <span className="cc-dot" />
              <span className="cc-dot" />
              <span className="cc-dot" />
            </div>
          </div>
        )}
      </div>

      <div className="cc-composer">
        <button
          type="button"
          className="cc-attach-btn"
          title="Upload complaint document (PDF, .txt, .eml)"
          onClick={() => fileInputRef.current?.click()}
          disabled={isThinking}
        >
          📎
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.eml"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
        <textarea
          className="cc-textarea"
          placeholder="e.g. Apollo Pharmacy reported discolored capsules in Amoxicillin 500mg…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isThinking}
        />
        <button
          type="button"
          className="cc-send-btn"
          onClick={handleSend}
          disabled={isThinking || !draft.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
