import { createSlice, createAsyncThunk, nanoid } from "@reduxjs/toolkit";
import { submitToCopilot, submitDocumentToCopilot } from "./complaintSlice";

export const sendUserMessage = createAsyncThunk(
  "chat/sendUserMessage",
  async (message, { dispatch }) => {
    const result = await dispatch(submitToCopilot({ message })).unwrap();
    return { reply: result.reply, tool_used: result.tool_used };
  }
);

export const sendUserDocument = createAsyncThunk(
  "chat/sendUserDocument",
  async ({ file, fileName }, { dispatch }) => {
    const result = await dispatch(submitDocumentToCopilot({ file })).unwrap();
    return { reply: result.reply, tool_used: result.tool_used, fileName };
  }
);

const initialMessages = [
  {
    id: "welcome",
    role: "assistant",
    content:
      "Hi, I'm AIVOA Copilot. Describe a customer complaint in your own words, or upload a complaint PDF/email, and I'll fill out the form and assess the risk for you.",
    toolUsed: null,
  },
];

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    messages: initialMessages,
    isThinking: false,
    error: null,
  },
  reducers: {
    resetChat: (state) => {
      state.messages = initialMessages;
      state.isThinking = false;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendUserMessage.pending, (state, action) => {
        state.isThinking = true;
        state.error = null;
        state.messages.push({
          id: nanoid(),
          role: "user",
          content: action.meta.arg,
          toolUsed: null,
        });
      })
      .addCase(sendUserMessage.fulfilled, (state, action) => {
        state.isThinking = false;
        state.messages.push({
          id: nanoid(),
          role: "assistant",
          content: action.payload.reply,
          toolUsed: action.payload.tool_used,
        });
      })
      .addCase(sendUserMessage.rejected, (state, action) => {
        state.isThinking = false;
        state.error = action.error.message;
        state.messages.push({
          id: nanoid(),
          role: "assistant",
          content:
            "Something went wrong reaching the AI service. Please check the backend is running and your GROQ_API_KEY is set, then try again.",
          toolUsed: null,
          isError: true,
        });
      })
      .addCase(sendUserDocument.pending, (state, action) => {
        state.isThinking = true;
        state.error = null;
        state.messages.push({
          id: nanoid(),
          role: "user",
          content: `📎 Uploaded document: ${action.meta.arg.fileName}`,
          toolUsed: null,
        });
      })
      .addCase(sendUserDocument.fulfilled, (state, action) => {
        state.isThinking = false;
        state.messages.push({
          id: nanoid(),
          role: "assistant",
          content: action.payload.reply,
          toolUsed: action.payload.tool_used,
        });
      })
      .addCase(sendUserDocument.rejected, (state, action) => {
        state.isThinking = false;
        state.error = action.error.message;
        state.messages.push({
          id: nanoid(),
          role: "assistant",
          content:
            "I couldn't process that document. Make sure it's a PDF, .txt, or .eml file with readable text, then try again.",
          toolUsed: null,
          isError: true,
        });
      });
  },
});

export const { resetChat } = chatSlice.actions;
export default chatSlice.reducer;
