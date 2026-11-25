
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function IntakePage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    category: "",
    description: "",
    currentLevel: "",
    interests: "",
    timeline: "",
    hours: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    setError("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (form.title.trim().length < 3) {
      setError("Please enter a dream title with at least 3 characters.");
      return;
    }

    if (form.description.trim().length < 10) {
      setError("Please describe your dream in at least 10 characters.");
      return;
    }

    if (form.interests.trim().length < 3) {
      setError("Please enter your interests and skills.");
      return;
    }

    setLoading(true);

    try {
      const savedData = localStorage.getItem("aspiraDreams");
      const existingDreams = savedData
        ? JSON.parse(savedData)
        : [];

      if (!Array.isArray(existingDreams)) {
        throw new Error("Invalid dream data");
      }

      const newDream = {
        id: Date.now().toString(),
        title: form.title.trim(),
        category: form.category,
        description: form.description.trim(),
        currentLevel: form.currentLevel,
        interests: form.interests.trim(),
        timeline: form.timeline,
        hours: form.hours,
        roadmapTasks: [],
        createdAt: new Date().toISOString(),
      };

      const updatedDreams = [...existingDreams, newDream];

      localStorage.setItem(
        "aspiraDreams",
        JSON.stringify(updatedDreams)
      );

      navigate("/dreams");
    } catch (err) {
      console.error("Dream saving error:", err);
      setError("Unable to save your dream. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="intake-page">

      {/* Header */}
      <header className="intake-header">
        <h2>
          ASPIRA<span style={{ color: "#20243a" }}>.</span>
        </h2>

        <button
          type="button"
          onClick={() => navigate("/dreams")}
        >
          ← Back to Dashboard
        </button>
      </header>

      <main className="intake-container">

        {/* Page Heading */}
        <div className="intake-heading">
          <span>YOUR FUTURE STARTS HERE</span>

          <h1>Let's define your dream.</h1>

          <p>
            Every great achievement begins with a clear goal.
            Share your aspirations and let us help you build a path forward.
          </p>
        </div>

        {/* Progress Indicator */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "12px",
            color: "#85899c",
            fontSize: "12px",
          }}
        >
          <span>Dream creation</span>
          <span>Step 1 of 1</span>
        </div>

        <div
          style={{
            height: "5px",
            background: "#e8e5fa",
            borderRadius: "10px",
            marginBottom: "25px",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              background: "#6558d3",
              borderRadius: "10px",
            }}
          />
        </div>

        {/* Dream Form */}
        <form className="intake-form" onSubmit={handleSubmit}>

          {/* Section 1 */}
          <section className="form-section">
            <h3>01 — Define your aspiration</h3>

            <label htmlFor="title">
              What do you want to achieve?
            </label>

            <input
              id="title"
              type="text"
              name="title"
              placeholder="e.g. Become a Software Developer"
              value={form.title}
              onChange={handleChange}
              required
            />

            <label htmlFor="category">
              Choose your career field
            </label>

            <select
              id="category"
              name="category"
              value={form.category}
              onChange={handleChange}
              required
            >
              <option value="">Select a career category</option>
              <option value="Technology">Technology</option>
              <option value="Engineering">Engineering</option>
              <option value="Medical">Medical and Healthcare</option>
              <option value="Business">Business and Management</option>
              <option value="Arts and Design">Arts and Design</option>
              <option value="Education">Education</option>
              <option value="Government">Government Services</option>
              <option value="Other">Other</option>
            </select>

            <label htmlFor="description">
              Tell us about your dream
            </label>

            <textarea
              id="description"
              name="description"
              placeholder="Describe what success looks like for you..."
              value={form.description}
              onChange={handleChange}
              rows="4"
              required
            />
          </section>

          {/* Section 2 */}
          <section className="form-section">
            <h3>02 — Understand your starting point</h3>

            <label htmlFor="currentLevel">
              How would you describe your current level?
            </label>

            <select
              id="currentLevel"
              name="currentLevel"
              value={form.currentLevel}
              onChange={handleChange}
              required
            >
              <option value="">Choose your experience level</option>
              <option value="Beginner">
                Beginner — Just getting started
              </option>
              <option value="Intermediate">
                Intermediate — Know the basics
              </option>
              <option value="Advanced">
                Advanced — Have good experience
              </option>
            </select>

            <label htmlFor="interests">
              What are your interests and skills?
            </label>

            <textarea
              id="interests"
              name="interests"
              placeholder="Mention your skills, interests, strengths or subjects you enjoy..."
              value={form.interests}
              onChange={handleChange}
              rows="4"
              required
            />
          </section>

          {/* Section 3 */}
          <section className="form-section">
            <h3>03 — Plan your commitment</h3>

            <label htmlFor="timeline">
              What is your target timeline?
            </label>

            <select
              id="timeline"
              name="timeline"
              value={form.timeline}
              onChange={handleChange}
              required
            >
              <option value="">Select your target timeline</option>
              <option value="3 months">Within 3 months</option>
              <option value="6 months">Within 6 months</option>
              <option value="1 year">Within 1 year</option>
              <option value="2 years">Within 2 years</option>
              <option value="Flexible">I'm flexible</option>
            </select>

            <label htmlFor="hours">
              How much time can you dedicate daily?
            </label>

            <select
              id="hours"
              name="hours"
              value={form.hours}
              onChange={handleChange}
              required
            >
              <option value="">Select daily commitment</option>
              <option value="1 hour">1 hour per day</option>
              <option value="2 hours">2 hours per day</option>
              <option value="3 hours">3 hours per day</option>
              <option value="4 hours">4 hours per day</option>
              <option value="5+ hours">5+ hours per day</option>
            </select>
          </section>

          {/* Error Message */}
          {error && (
            <p
              role="alert"
              style={{
                color: "#d9364f",
                marginBottom: "18px",
                fontSize: "13px",
              }}
            >
              {error}
            </p>
          )}

          {/* Form Buttons */}
          <div className="intake-actions">
            <button
              type="button"
              className="cancel-btn"
              onClick={() => navigate("/dreams")}
              disabled={loading}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="submit-btn"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save My Dream →"}
            </button>
          </div>

          <p
            style={{
              textAlign: "center",
              color: "#999",
              fontSize: "11px",
              marginTop: "20px",
            }}
          >
            Your goals are the beginning of your journey with ASPIRA.
          </p>

        </form>
      </main>
    </div>
  );
}

export default IntakePage;
