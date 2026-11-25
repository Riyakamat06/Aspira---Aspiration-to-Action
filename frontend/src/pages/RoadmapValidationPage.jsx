
import { useState } from "react";

function RoadmapValidationPage() {
  const [roadmap, setRoadmap] = useState("");
  const [careerGoal, setCareerGoal] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleValidate = () => {
    if (!careerGoal.trim()) {
      setResult({
        error: "Please enter your career goal first.",
      });
      return;
    }

    if (roadmap.trim().length < 30) {
      setResult({
        error: "Please enter a more detailed roadmap (at least 30 characters).",
      });
      return;
    }

    setLoading(true);
    setResult(null);

    // Demo validation logic until the backend API is connected
    setTimeout(() => {
      const text = roadmap.toLowerCase();

      const checks = [
        {
          title: "Learning & Fundamentals",
          keywords: ["learn", "fundamental", "basics", "course", "study"],
        },
        {
          title: "Technical Skills",
          keywords: ["skill", "programming", "technology", "coding", "tools"],
        },
        {
          title: "Practical Projects",
          keywords: ["project", "build", "develop", "portfolio", "application"],
        },
        {
          title: "Practice & Experience",
          keywords: ["practice", "internship", "experience", "exercise"],
        },
        {
          title: "Career Preparation",
          keywords: ["resume", "interview", "job", "placement", "certification"],
        },
        {
          title: "Timeline & Milestones",
          keywords: ["week", "month", "deadline", "milestone", "timeline"],
        },
      ];

      const matched = checks.filter((item) =>
        item.keywords.some((keyword) => text.includes(keyword))
      );

      const missing = checks.filter(
        (item) => !matched.includes(item)
      );

      const score = Math.round(
        (matched.length / checks.length) * 100
      );

      const validation = {
        score,
        matched,
        missing,
        goal: careerGoal.trim(),
        date: new Date().toLocaleDateString(),
      };

      setResult(validation);

      try {
        localStorage.setItem(
          "aspiraLastValidation",
          JSON.stringify({
            ...validation,
            roadmap,
          })
        );
      } catch (error) {
        console.error("Unable to save validation:", error);
      }

      setLoading(false);
    }, 800);
  };

  const resetForm = () => {
    setRoadmap("");
    setCareerGoal("");
    setResult(null);
  };

  return (
    <main style={styles.page}>
      <div style={styles.container}>

        {/* Header */}
        <header style={styles.header}>
          <span style={styles.label}>
            ASPIRA • ROADMAP REVIEW
          </span>

          <h1>Roadmap Validation ✨</h1>

          <p style={styles.subtitle}>
            Check your career roadmap, discover missing steps
            and make your journey towards success more structured.
          </p>
        </header>

        {/* Input Card */}
        <section style={styles.card}>
          <div style={styles.sectionTitle}>
            <span>📝</span>
            <h2>Submit Your Career Roadmap</h2>
          </div>

          <label style={styles.heading}>
            Your Career Goal
          </label>

          <input
            type="text"
            value={careerGoal}
            onChange={(e) => setCareerGoal(e.target.value)}
            placeholder="Example: Become a Full Stack Developer"
            style={styles.input}
          />

          <label style={styles.heading}>
            Your Roadmap
          </label>

          <textarea
            value={roadmap}
            onChange={(e) => setRoadmap(e.target.value)}
            placeholder={`Paste your career roadmap here...

Example:
1. Learn programming fundamentals.
2. Develop technical skills in HTML, CSS and JavaScript.
3. Build practical web development projects.
4. Practice coding and gain internship experience.
5. Prepare my resume and attend interviews.
6. Complete milestones within 6 months.`}
            style={styles.textarea}
            rows={10}
          />

          <div style={styles.wordCount}>
            {roadmap.trim()
              ? roadmap.trim().split(/\s+/).length
              : 0} words
          </div>

          <div style={styles.buttonRow}>
            <button
              onClick={handleValidate}
              disabled={loading}
              style={{
                ...styles.button,
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? "Reviewing Roadmap..." : "✨ Validate Roadmap"}
            </button>

            <button
              onClick={resetForm}
              style={styles.resetButton}
            >
              Reset
            </button>
          </div>
        </section>

        {/* Validation Results */}
        {result && (
          <section style={styles.resultCard}>
            {result.error ? (
              <div style={styles.error}>
                ⚠️ {result.error}
              </div>
            ) : (
              <>
                <div style={styles.resultHeader}>
                  <div>
                    <span style={styles.label}>
                      VALIDATION REPORT
                    </span>

                    <h2>Your Roadmap Analysis</h2>

                    <p style={styles.goalText}>
                      Career goal: {result.goal}
                    </p>
                  </div>

                  <div style={styles.scoreCircle}>
                    <strong>{result.score}%</strong>
                    <span>Completeness</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div style={styles.progressTrack}>
                  <div
                    style={{
                      ...styles.progressFill,
                      width: `${result.score}%`,
                    }}
                  />
                </div>

                <p style={styles.scoreMessage}>
                  {result.score >= 80
                    ? "Excellent! Your roadmap covers most important areas."
                    : result.score >= 50
                    ? "Good start! A few important areas need attention."
                    : "Your roadmap needs more details and career-planning steps."}
                </p>

                {/* Strengths */}
                <div style={styles.feedbackSection}>
                  <h3>✅ Strengths Identified</h3>

                  {result.matched.length > 0 ? (
                    result.matched.map((item, index) => (
                      <div key={index} style={styles.feedbackItem}>
                        <span>✓</span>
                        {item.title}
                      </div>
                    ))
                  ) : (
                    <p style={styles.emptyText}>
                      No major roadmap elements were identified yet.
                    </p>
                  )}
                </div>

                {/* Missing Areas */}
                <div style={styles.feedbackSection}>
                  <h3>⚠️ Areas to Improve</h3>

                  {result.missing.length > 0 ? (
                    result.missing.map((item, index) => (
                      <div
                        key={index}
                        style={styles.missingItem}
                      >
                        <span>＋</span>
                        Add {item.title.toLowerCase()}
                      </div>
                    ))
                  ) : (
                    <p style={styles.successText}>
                      Great! All six roadmap areas are covered.
                    </p>
                  )}
                </div>

                {/* Suggestions */}
                <div style={styles.suggestionBox}>
                  <h3>💡 ASPIRA Suggestions</h3>

                  <ul>
                    <li>Break large goals into smaller achievable tasks.</li>
                    <li>Set realistic deadlines for every milestone.</li>
                    <li>Include practical projects to demonstrate your skills.</li>
                    <li>Review and update your roadmap regularly.</li>
                  </ul>
                </div>

                <p style={styles.disclaimer}>
                  This is a preliminary keyword-based demo review,
                  not an AI assessment. Actual career-specific validation
                  will be connected through the backend API.
                </p>

                <button
                  onClick={resetForm}
                  style={styles.button}
                >
                  Validate Another Roadmap →
                </button>
              </>
            )}
          </section>
        )}

        {/* Tip */}
        <div style={styles.tip}>
          💡 <strong>Tip:</strong> A strong career roadmap should
          include learning, skills, projects, practice, career
          preparation and realistic milestones.
        </div>
      </div>
    </main>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    padding: "40px 20px",
    background: "linear-gradient(135deg, #f5efff, #eee5ff)",
    fontFamily: "Arial, sans-serif",
  },
  container: {
    maxWidth: "900px",
    margin: "auto",
  },
  header: {
    marginBottom: "28px",
  },
  label: {
    color: "#9169d5",
    fontSize: "12px",
    fontWeight: "bold",
    letterSpacing: "1.5px",
  },
  subtitle: {
    color: "#81758f",
    lineHeight: "1.7",
    maxWidth: "700px",
  },
  card: {
    background: "#fff",
    padding: "30px",
    borderRadius: "20px",
    boxShadow: "0 10px 30px rgba(89,54,145,0.09)",
  },
  sectionTitle: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    marginBottom: "25px",
    color: "#49316d",
  },
  heading: {
    display: "block",
    color: "#49316d",
    fontWeight: "bold",
    marginBottom: "10px",
    marginTop: "18px",
    fontSize: "14px",
  },
  input: {
    width: "100%",
    boxSizing: "border-box",
    padding: "14px",
    border: "1px solid #e2d9f3",
    borderRadius: "11px",
    fontSize: "14px",
    outlineColor: "#9872e5",
    background: "#fcfbff",
  },
  textarea: {
    width: "100%",
    boxSizing: "border-box",
    padding: "15px",
    border: "1px solid #e2d9f3",
    borderRadius: "12px",
    background: "#fcfbff",
    fontSize: "14px",
    lineHeight: "1.7",
    resize: "vertical",
    outlineColor: "#9872e5",
  },
  wordCount: {
    textAlign: "right",
    color: "#9589a6",
    fontSize: "12px",
    marginTop: "7px",
  },
  buttonRow: {
    display: "flex",
    gap: "12px",
    flexWrap: "wrap",
    marginTop: "20px",
  },
  button: {
    padding: "13px 23px",
    border: "none",
    borderRadius: "10px",
    background: "linear-gradient(135deg, #8055d9, #a47be9)",
    color: "#fff",
    fontWeight: "bold",
    cursor: "pointer",
  },
  resetButton: {
    padding: "13px 23px",
    border: "1px solid #ddd3f1",
    borderRadius: "10px",
    background: "#fff",
    color: "#7252b1",
    fontWeight: "bold",
    cursor: "pointer",
  },
  resultCard: {
    marginTop: "25px",
    background: "#fff",
    padding: "30px",
    borderRadius: "20px",
    boxShadow: "0 10px 30px rgba(89,54,145,0.08)",
  },
  resultHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "20px",
    flexWrap: "wrap",
  },
  goalText: {
    color: "#81758f",
    fontSize: "14px",
  },
  scoreCircle: {
    width: "105px",
    height: "105px",
    borderRadius: "50%",
    background: "#f0eaff",
    color: "#7047bc",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    flexShrink: 0,
  },
  progressTrack: {
    height: "11px",
    background: "#eee8f8",
    borderRadius: "20px",
    marginTop: "25px",
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    background: "linear-gradient(90deg, #9c78e7, #6447bd)",
    borderRadius: "20px",
    transition: "width 0.5s ease",
  },
  scoreMessage: {
    color: "#7252b1",
    fontSize: "14px",
    marginTop: "13px",
  },
  feedbackSection: {
    marginTop: "28px",
  },
  feedbackItem: {
    padding: "12px",
    background: "#effaf4",
    color: "#27794e",
    borderRadius: "9px",
    marginTop: "9px",
    display: "flex",
    gap: "10px",
    fontSize: "14px",
  },
  missingItem: {
    padding: "12px",
    background: "#fff7e9",
    color: "#a66a19",
    borderRadius: "9px",
    marginTop: "9px",
    display: "flex",
    gap: "10px",
    fontSize: "14px",
  },
  emptyText: {
    color: "#81758f",
    fontSize: "14px",
  },
  successText: {
    color: "#27794e",
    fontSize: "14px",
  },
  suggestionBox: {
    marginTop: "28px",
    padding: "20px",
    borderRadius: "13px",
    background: "#f4efff",
    color: "#56358e",
    lineHeight: "1.9",
    fontSize: "14px",
  },
  disclaimer: {
    color: "#9589a6",
    fontSize: "12px",
    lineHeight: "1.6",
    marginTop: "22px",
  },
  error: {
    padding: "15px",
    background: "#fff0f0",
    color: "#c53030",
    borderRadius: "10px",
  },
  tip: {
    marginTop: "22px",
    padding: "17px",
    background: "#fff",
    borderRadius: "12px",
    color: "#75668a",
    fontSize: "13px",
    lineHeight: "1.6",
  },
};

export default RoadmapValidationPage;

