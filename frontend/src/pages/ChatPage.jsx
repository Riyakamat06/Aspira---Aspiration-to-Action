
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const suggestions = [
  "How can I become a Web Developer?",
  "What skills are required for Data Science?",
  "Suggest projects for beginners.",
  "How should I prepare for placements?",
];

const welcomeMessage = {
  role: "assistant",
  text: "Hello! 👋 Welcome to ASPIRA Career Assistant. I'm here to help you explore career paths, learn new skills and plan your future. What would you like to know?",
};

function ChatPage() {
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);

  const [messages, setMessages] = useState(() => {
    try {
      const saved = JSON.parse(
        localStorage.getItem("aspiraChatHistory") || "null"
      );

      return Array.isArray(saved) && saved.length > 0
        ? saved
        : [welcomeMessage];
    } catch {
      return [welcomeMessage];
    }
  });

  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  // Save chat history
  useEffect(() => {
    try {
      localStorage.setItem(
        "aspiraChatHistory",
        JSON.stringify(messages)
      );
    } catch (error) {
      console.error("Unable to save chat history:", error);
    }
  }, [messages]);

  // Scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isTyping]);

  // Career responses
  const getResponse = (question) => {
    const text = question.toLowerCase();

    if (
      text.includes("web developer") ||
      text.includes("web development")
    ) {
      return "🌐 WEB DEVELOPMENT ROADMAP\n\n1. HTML – Learn webpage structure.\n2. CSS – Learn styling and responsive design.\n3. JavaScript – Understand programming and interactivity.\n4. React – Build modern frontend applications.\n5. Node.js and Express – Learn backend development.\n6. MongoDB or SQL – Understand databases.\n\n💡 Practice by building a portfolio, task manager and e-commerce website. Upload your projects to GitHub!";
    }

    if (
      text.includes("data science") ||
      text.includes("data scientist")
    ) {
      return "📊 DATA SCIENCE ROADMAP\n\n1. Learn Python programming.\n2. Study statistics and mathematics.\n3. Learn SQL and database concepts.\n4. Practice Pandas and NumPy.\n5. Explore Matplotlib and data visualization.\n6. Understand machine learning.\n\n💡 Beginner projects: Sales prediction, customer analysis and student performance analysis.";
    }

    if (
      text.includes("project") ||
      text.includes("projects")
    ) {
      return "💡 BEGINNER PROJECT IDEAS\n\n1. Personal Portfolio Website.\n2. Expense Tracker.\n3. Online Quiz Application.\n4. Career Roadmap Planner.\n5. Weather Dashboard.\n6. Learning Journal.\n7. Online Book Store.\n\nChoose a project, identify its features, design the interface, develop it and test it before publishing it on GitHub.";
    }

    if (
      text.includes("placement") ||
      text.includes("interview")
    ) {
      return "🎓 PLACEMENT PREPARATION PLAN\n\n1. Programming: C, Java or Python fundamentals.\n2. Aptitude: Percentages, ratios, time and work, reasoning.\n3. Technical subjects: DBMS, OOP, Operating Systems and Computer Networks.\n4. English: Grammar, vocabulary and communication.\n5. Coding: Practice basic programming problems.\n6. Interview: Prepare your self-introduction and project explanation.\n\n💡 Practice consistently and attend mock interviews.";
    }

    if (
      text.includes("engineer") ||
      text.includes("engineering")
    ) {
      return "⚙️ ENGINEERING CAREER OPTIONS\n\nYou can explore:\n1. Computer Science Engineering.\n2. Mechanical Engineering.\n3. Civil Engineering.\n4. Electrical Engineering.\n5. Electronics Engineering.\n\nResearch the qualifications, entrance requirements and job opportunities for your preferred branch. Build practical skills through projects and internships.";
    }

    if (
      text.includes("medical") ||
      text.includes("doctor")
    ) {
      return "🩺 MEDICAL CAREER OPTIONS\n\nSome career paths include:\n1. Doctor.\n2. Nursing.\n3. Pharmacy.\n4. Physiotherapy.\n5. Medical Laboratory Technology.\n6. Medical Research.\n\nCheck the required qualifications, entrance examinations and training for your chosen career before making a plan.";
    }

    if (
      text.includes("skill") ||
      text.includes("learn")
    ) {
      return "🚀 HOW TO DEVELOP YOUR SKILLS\n\n1. Select one career goal.\n2. Identify the important skills.\n3. Divide skills into beginner, intermediate and advanced levels.\n4. Follow a weekly learning schedule.\n5. Practice with small exercises.\n6. Build real-world projects.\n7. Review your progress every week.\n\nRemember: Consistency is more important than learning everything at once!";
    }

    if (
      text.includes("resume") ||
      text.includes("cv")
    ) {
      return "📄 RESUME PREPARATION TIPS\n\n1. Add your name and contact details.\n2. Write a short career objective.\n3. Mention your education.\n4. List your technical skills.\n5. Include academic and personal projects.\n6. Add internships or certifications if available.\n7. Check spelling and formatting.\n\n💡 Keep your resume clear, honest and preferably one page if you are a fresher.";
    }

    if (
      text.includes("hello") ||
      text.includes("hi") ||
      text.includes("hey")
    ) {
      return "Hello! 😊 It's great to have you here. What would you like help with today? You can ask me about career options, programming, projects, skills or placements.";
    }

    return "That's an interesting question! 😊\n\nTo guide you better, tell me a little more about your career goal or the skill you want to learn.\n\nI can help you explore:\n• Web Development\n• Data Science\n• Engineering careers\n• Medical careers\n• Beginner projects\n• Resume preparation\n• Placement preparation\n\nLet's plan your next step together!";
  };

  // Send message
  const sendMessage = (message = input) => {
    const question = message.trim();

    if (!question || isTyping) return;

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: question,
      },
    ]);

    setInput("");
    setIsTyping(true);

    // Demo response delay
    setTimeout(() => {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: getResponse(question),
        },
      ]);

      setIsTyping(false);
    }, 700);
  };

  // Clear chat
  const clearChat = () => {
    setMessages([welcomeMessage]);
    setInput("");
    setIsTyping(false);
  };

  return (
    <main style={styles.page}>
      <div style={styles.container}>

        <button
          style={styles.back}
          onClick={() => navigate("/dreams")}
        >
          ← Back to Dashboard
        </button>

        {/* Heading */}
        <header style={styles.header}>
          <div style={styles.avatar}>✧</div>

          <div>
            <span style={styles.eyebrow}>
              ASPIRA CAREER ASSISTANT
            </span>

            <h1>Your Career Companion</h1>

            <p style={styles.subtitle}>
              Explore possibilities. Discover skills. Plan your future.
            </p>
          </div>
        </header>

        {/* Chat Container */}
        <section style={styles.chatCard}>

          {/* Chat Header */}
          <div style={styles.chatHeader}>
            <div style={styles.botInfo}>
              <div style={styles.smallHeaderAvatar}>✧</div>

              <div>
                <strong>Career Assistant</strong>
                <p>Here to help you move forward</p>
              </div>
            </div>

            <div style={styles.headerActions}>
              <span style={styles.online}>
                ● Available
              </span>

              <button
                type="button"
                style={styles.clearButton}
                onClick={clearChat}
              >
                Clear chat
              </button>
            </div>
          </div>

          {/* Messages */}
          <div style={styles.messages}>
            {messages.map((message, index) => (
              <div
                key={index}
                style={{
                  ...styles.messageRow,
                  justifyContent:
                    message.role === "user"
                      ? "flex-end"
                      : "flex-start",
                }}
              >
                {message.role === "assistant" && (
                  <div style={styles.smallAvatar}>✧</div>
                )}

                <div
                  style={{
                    ...styles.bubble,
                    ...(message.role === "user"
                      ? styles.userBubble
                      : styles.assistantBubble),
                  }}
                >
                  {message.text}
                </div>
              </div>
            ))}

            {isTyping && (
              <div style={styles.messageRow}>
                <div style={styles.smallAvatar}>✧</div>

                <div style={styles.typingBubble}>
                  Assistant is typing...
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Questions */}
          {messages.length === 1 && (
            <div style={styles.suggestions}>
              <p style={styles.suggestionTitle}>
                ✨ Try asking:
              </p>

              <div style={styles.suggestionList}>
                {suggestions.map((suggestion) => (
                  <button
                    type="button"
                    key={suggestion}
                    style={styles.suggestion}
                    onClick={() => sendMessage(suggestion)}
                    disabled={isTyping}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <form
            style={styles.inputArea}
            onSubmit={(event) => {
              event.preventDefault();
              sendMessage();
            }}
          >
            <input
              style={styles.input}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask anything about your career..."
              disabled={isTyping}
              aria-label="Type your career question"
            />

            <button
              type="submit"
              style={{
                ...styles.sendButton,
                opacity: input.trim() && !isTyping ? 1 : 0.6,
              }}
              disabled={!input.trim() || isTyping}
            >
              Send ↑
            </button>
          </form>

        </section>

        {/* Disclaimer */}
        <p style={styles.disclaimer}>
          Demo assistant: Responses are predefined examples, not live
          AI-generated advice. An AI service can be connected through
          the backend in a later integration step.
        </p>

      </div>
    </main>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #f7f6ff, #f4f6fc)",
    padding: "35px 20px",
  },
  container: {
    maxWidth: "900px",
    margin: "0 auto",
  },
  back: {
    border: "none",
    background: "transparent",
    color: "#6558d3",
    fontWeight: "600",
    cursor: "pointer",
    marginBottom: "25px",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: "18px",
    marginBottom: "25px",
  },
  avatar: {
    width: "60px",
    height: "60px",
    background: "linear-gradient(135deg, #887ce9, #5144bd)",
    color: "white",
    borderRadius: "17px",
    display: "grid",
    placeItems: "center",
    fontSize: "30px",
    flexShrink: 0,
    boxShadow: "0 6px 15px rgba(101,88,211,0.2)",
  },
  eyebrow: {
    color: "#6558d3",
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "2px",
  },
  subtitle: {
    color: "#85869a",
    fontSize: "13px",
    lineHeight: 1.6,
  },
  chatCard: {
    background: "white",
    border: "1px solid #ececf4",
    borderRadius: "18px",
    overflow: "hidden",
    boxShadow: "0 8px 30px rgba(50,40,100,0.06)",
  },
  chatHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "12px",
    padding: "20px 25px",
    borderBottom: "1px solid #eeeeF5",
  },
  botInfo: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  smallHeaderAvatar: {
    width: "40px",
    height: "40px",
    borderRadius: "13px",
    background: "#eeedff",
    color: "#6558d3",
    display: "grid",
    placeItems: "center",
    fontSize: "22px",
  },
  headerActions: {
    display: "flex",
    alignItems: "center",
    gap: "15px",
    flexWrap: "wrap",
  },
  online: {
    color: "#299b72",
    fontSize: "12px",
  },
  clearButton: {
    border: "1px solid #e8e4fa",
    background: "#faf9ff",
    color: "#6558d3",
    padding: "8px 12px",
    borderRadius: "9px",
    fontSize: "12px",
    cursor: "pointer",
  },
  messages: {
    minHeight: "300px",
    maxHeight: "450px",
    overflowY: "auto",
    padding: "25px",
    display: "flex",
    flexDirection: "column",
    gap: "18px",
    background: "#fcfcff",
  },
  messageRow: {
    display: "flex",
    alignItems: "flex-start",
    gap: "10px",
  },
  smallAvatar: {
    width: "30px",
    height: "30px",
    borderRadius: "10px",
    background: "#eeedff",
    color: "#6558d3",
    display: "grid",
    placeItems: "center",
    flexShrink: 0,
  },
  bubble: {
    maxWidth: "82%",
    padding: "13px 16px",
    borderRadius: "13px",
    fontSize: "14px",
    lineHeight: 1.8,
    whiteSpace: "pre-wrap",
    overflowWrap: "anywhere",
  },
  assistantBubble: {
    background: "#f0efff",
    color: "#42415c",
    borderTopLeftRadius: "3px",
  },
  userBubble: {
    background: "linear-gradient(135deg, #7567df, #5144bd)",
    color: "white",
    borderTopRightRadius: "3px",
  },
  typingBubble: {
    background: "#f0efff",
    color: "#85869a",
    padding: "12px 15px",
    borderRadius: "12px",
    fontSize: "12px",
  },
  suggestions: {
    padding: "18px 22px",
    borderTop: "1px solid #eeeeF5",
  },
  suggestionTitle: {
    color: "#5144bd",
    fontSize: "13px",
    fontWeight: "600",
  },
  suggestionList: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
  },
  suggestion: {
    padding: "9px 12px",
    border: "1px solid #e4e1fa",
    borderRadius: "20px",
    background: "white",
    color: "#6558d3",
    fontSize: "12px",
    cursor: "pointer",
  },
  inputArea: {
    display: "flex",
    gap: "10px",
    padding: "18px",
    borderTop: "1px solid #eeeeF5",
  },
  input: {
    flex: 1,
    minWidth: 0,
    border: "1px solid #dedee9",
    borderRadius: "10px",
    padding: "13px",
    fontSize: "14px",
    outlineColor: "#6558d3",
  },
  sendButton: {
    border: "none",
    borderRadius: "10px",
    padding: "0 20px",
    background: "#6558d3",
    color: "white",
    fontWeight: "600",
    cursor: "pointer",
  },
  disclaimer: {
    textAlign: "center",
    color: "#85869a",
    fontSize: "12px",
    lineHeight: 1.6,
    marginTop: "18px",
  },
};

export default ChatPage;
