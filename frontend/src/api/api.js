import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE });

export const sendChatMessage = (message, complaintId) =>
  client.post("/api/chat", { message, complaint_id: complaintId }).then((r) => r.data);

export const uploadDocument = (file, complaintId) => {
  const formData = new FormData();
  formData.append("file", file);
  if (complaintId) formData.append("complaint_id", complaintId);
  return client
    .post("/api/upload/document", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};

export default client;
