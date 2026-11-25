
import apiClient from "./apiClient";

const chatApi = {
  // Send a message to the chatbot
  sendMessage: (message, conversationId = null) =>
    apiClient.post("/chat", {
      message,
      conversation_id: conversationId,
    }),

  // Get previous chat messages
  getChatHistory: (conversationId) =>
    apiClient.get(`/chat/${conversationId}`),

  // Delete a conversation
  deleteConversation: (conversationId) =>
    apiClient.delete(`/chat/${conversationId}`),
};

export default chatApi;
