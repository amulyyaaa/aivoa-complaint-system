import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { sendChatMessage, uploadDocument } from "../api/api";

const initialFormState = {
  id: null,
  status: null,
  customer_name: null,
  product_name: null,
  product_strength: null,
  batch_number: null,
  manufacturing_date: null,
  expiry_date: null,
  affected_quantity: null,
  complaint_type: null,
  complaint_description: null,
  date_reported: null,
  source_channel: null,
  // AI Copilot Risk Assessment
  severity: null,
  risk_category: null,
  recommended_next_action: null,
  recommended_capa: null,
  ai_reasoning_summary: null,
};

export const submitToCopilot = createAsyncThunk(
  "complaint/submitToCopilot",
  async ({ message }, { getState }) => {
    const complaintId = getState().complaint.form.id;
    return sendChatMessage(message, complaintId);
  }
);

export const submitDocumentToCopilot = createAsyncThunk(
  "complaint/submitDocumentToCopilot",
  async ({ file }, { getState }) => {
    const complaintId = getState().complaint.form.id;
    return uploadDocument(file, complaintId);
  }
);

const complaintSlice = createSlice({
  name: "complaint",
  initialState: {
    form: initialFormState,
    status: "idle", // idle | loading | failed
    error: null,
    lastToolUsed: null,
  },
  reducers: {
    resetComplaint: (state) => {
      state.form = initialFormState;
      state.status = "idle";
      state.error = null;
      state.lastToolUsed = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitToCopilot.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(submitToCopilot.fulfilled, (state, action) => {
        state.status = "idle";
        state.form = action.payload.complaint;
        state.lastToolUsed = action.payload.tool_used;
      })
      .addCase(submitToCopilot.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      })
      .addCase(submitDocumentToCopilot.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(submitDocumentToCopilot.fulfilled, (state, action) => {
        state.status = "idle";
        state.form = action.payload.complaint;
        state.lastToolUsed = action.payload.tool_used;
      })
      .addCase(submitDocumentToCopilot.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export const { resetComplaint } = complaintSlice.actions;
export default complaintSlice.reducer;
