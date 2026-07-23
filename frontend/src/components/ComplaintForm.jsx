import React from "react";
import { useSelector } from "react-redux";
import "./ComplaintForm.css";

const FIELD_GROUPS = [
  {
    title: "Customer & Product",
    fields: [
      ["customer_name", "Customer / Reporting Site"],
      ["product_name", "Product Name"],
      ["product_strength", "Strength / Grade"],
    ],
  },
  {
    title: "Batch Traceability",
    fields: [
      ["batch_number", "Batch / Lot Number", true],
      ["manufacturing_date", "Manufacturing Date"],
      ["expiry_date", "Expiry Date"],
      ["affected_quantity", "Affected Quantity"],
    ],
  },
  {
    title: "Complaint Details",
    fields: [
      ["complaint_type", "Complaint Type"],
      ["date_reported", "Date Reported"],
      ["complaint_description", "Description", false, true],
    ],
  },
];

function Field({ label, value, mono, multiline }) {
  const empty = value === null || value === undefined || value === "";
  return (
    <label className="cf-field">
      <span className="cf-label">{label}</span>
      {multiline ? (
        <textarea
          className={`cf-input cf-textarea ${empty ? "cf-empty" : ""}`}
          value={value || ""}
          placeholder="Awaiting AI Copilot input…"
          readOnly
          rows={3}
        />
      ) : (
        <input
          className={`cf-input ${mono ? "mono" : ""} ${empty ? "cf-empty" : ""}`}
          value={value || ""}
          placeholder="Awaiting AI Copilot input…"
          readOnly
        />
      )}
    </label>
  );
}

export default function ComplaintForm() {
  const form = useSelector((s) => s.complaint.form);

  return (
    <div className="cf-panel">
      <div className="cf-header">
        <div>
          <h1 className="cf-title">Log Customer Complaint</h1>
          <p className="cf-subtitle">
            Filled automatically by AIVOA Copilot — describe the complaint on the right.
          </p>
        </div>
        <div className="cf-idbox">
          <span className="cf-id-label">Complaint ID</span>
          <span className="cf-id-value mono">
            {form.id ? form.id.slice(0, 8).toUpperCase() : "—"}
          </span>
          {form.status && <span className="cf-status">{form.status}</span>}
        </div>
      </div>

      <div className="cf-body">
        {FIELD_GROUPS.map((group) => (
          <section className="cf-group" key={group.title}>
            <h2 className="cf-group-title">{group.title}</h2>
            <div className="cf-grid">
              {group.fields.map(([key, label, mono, multiline]) => (
                <div
                  className={multiline ? "cf-grid-full" : ""}
                  key={key}
                >
                  <Field
                    label={label}
                    value={form[key]}
                    mono={mono}
                    multiline={multiline}
                  />
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
