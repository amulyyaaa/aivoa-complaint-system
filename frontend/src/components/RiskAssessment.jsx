import React from "react";
import { useSelector } from "react-redux";
import "./RiskAssessment.css";

const SEVERITY_STYLE = {
  Critical: { cls: "sev-critical", dot: "●" },
  Major: { cls: "sev-major", dot: "●" },
  Minor: { cls: "sev-minor", dot: "●" },
};

export default function RiskAssessment() {
  const form = useSelector((s) => s.complaint.form);
  const hasAssessment = Boolean(form.severity);
  const sevStyle = SEVERITY_STYLE[form.severity] || { cls: "sev-neutral", dot: "○" };

  return (
    <div className="ra-card">
      <div className="ra-card-head">
        <span className="ra-eyebrow">AI Copilot · Risk Assessment</span>
        {hasAssessment ? (
          <span className={`ra-badge ${sevStyle.cls}`}>
            <span aria-hidden="true">{sevStyle.dot}</span> {form.severity}
          </span>
        ) : (
          <span className="ra-badge sev-neutral">Not yet assessed</span>
        )}
      </div>

      {hasAssessment ? (
        <div className="ra-body">
          <div className="ra-row">
            <span className="ra-row-label">Risk category</span>
            <span className="ra-row-value">{form.risk_category || "—"}</span>
          </div>
          <div className="ra-row">
            <span className="ra-row-label">Next action</span>
            <span className="ra-row-value">{form.recommended_next_action || "—"}</span>
          </div>
          <div className="ra-row">
            <span className="ra-row-label">CAPA suggestion</span>
            <span className="ra-row-value">{form.recommended_capa || "—"}</span>
          </div>
          {form.ai_reasoning_summary && (
            <p className="ra-reasoning">“{form.ai_reasoning_summary}”</p>
          )}
        </div>
      ) : (
        <p className="ra-empty">
          Describe a complaint in the chat below and the Copilot will classify severity,
          category, and recommended next steps here.
        </p>
      )}
    </div>
  );
}
