
import React, { useState } from "react";
import chatApi from "../api/chatApi";
import "./ChatWindow.css";

const ChatWindow = () => {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! 👋 Welcome to ASPIRA. What career goal can I help you with today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);

  const sendMessage = async (e) => {
    e.preventDefault();

    if (!input.trim() || loading) return;

    const userMessage = input.trim();

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(
        userMessage,
        conversationId
      );

      setConversationId(
        response.conversation_id || conversationId
      );

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            response.reply ||
            response.message ||
            "I received your message.",
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry! Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="chat-avatar">✦</div>
        <div>
          <h3>ASPIRA AI Assistant</h3>
          <span>Career guidance companion</span>
        </div>
        <span className="online-dot"></span>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role}`}
          >
            <div className="message-bubble">
              {message.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-bubble typing">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form className="chat-input-area" onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your career..."
          disabled={loading}
        />

        <button type="submit" disabled={loading || !input.trim()}>
          ➤
        </button>
      </form>
    </div>
  );
};

export default ChatWindow;
