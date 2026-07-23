import React from "react";
import { useDispatch, useSelector } from "react-redux";
import ComplaintForm from "./components/ComplaintForm";
import CopilotChat from "./components/CopilotChat";
import { resetComplaint } from "./store/complaintSlice";
import { resetChat } from "./store/chatSlice";
import "./App.css";

export default function App() {
  const dispatch = useDispatch();
  const complaintId = useSelector((s) => s.complaint.form.id);

  const handleNewComplaint = () => {
    dispatch(resetComplaint());
    dispatch(resetChat());
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-brand">
          <span className="app-brand-mark">AIVOA</span>
          <span className="app-brand-divider">|</span>
          <span className="app-brand-name">Customer Complaint Management</span>
        </div>
        <button className="app-new-btn" onClick={handleNewComplaint} disabled={!complaintId}>
          + New Complaint
        </button>
      </header>

      <main className="app-body">
        <section className="app-pane app-pane-form">
          <ComplaintForm />
        </section>
        <section className="app-pane app-pane-chat">
          <CopilotChat />
        </section>
      </main>
    </div>
  );
}
