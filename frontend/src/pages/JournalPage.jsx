
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const getEmptyForm = () => ({
  title: "",
  date: new Date().toISOString().split("T")[0],
  category: "Learning",
  content: "",
  mood: "😊",
});

function JournalPage() {
  const navigate = useNavigate();

  const [entries, setEntries] = useState([]);
  const [form, setForm] = useState(getEmptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  // Load saved journal entries
  useEffect(() => {
    try {
      const savedEntries = JSON.parse(
        localStorage.getItem("aspiraJournal") || "[]"
      );

      setEntries(
        Array.isArray(savedEntries) ? savedEntries : []
      );
    } catch (err) {
      console.error("Journal loading error:", err);
      setEntries([]);
      setError("Unable to load your journal entries.");
    }
  }, []);

  // Handle form changes
  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    setError("");
  };

  // Save entries to localStorage
  const saveEntries = (updatedEntries) => {
    try {
      localStorage.setItem(
        "aspiraJournal",
        JSON.stringify(updatedEntries)
      );

      setEntries(updatedEntries);
      return true;
    } catch (err) {
      console.error("Journal saving error:", err);
      setError("Unable to save your entry. Please try again.");
      return false;
    }
  };

  // Add or update an entry
  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (form.title.trim().length < 3) {
      setError("Please enter a title with at least 3 characters.");
      return;
    }

    if (form.content.trim().length < 10) {
      setError("Please write at least 10 characters about your learning.");
      return;
    }

    let updatedEntries;

    if (editingId !== null) {
      updatedEntries = entries.map((entry) =>
        String(entry.id) === String(editingId)
          ? {
              ...entry,
              ...form,
              title: form.title.trim(),
              content: form.content.trim(),
              updatedAt: new Date().toISOString(),
            }
          : entry
      );
    } else {
      const newEntry = {
        ...form,
        title: form.title.trim(),
        content: form.content.trim(),
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
      };

      updatedEntries = [newEntry, ...entries];
    }

    if (saveEntries(updatedEntries)) {
      cancelEdit();
    }
  };

  // Load an entry into the form for editing
  const handleEdit = (entry) => {
    setEditingId(entry.id);

    setForm({
      title: entry.title || "",
      date: entry.date || "",
      category: entry.category || "Learning",
      content: entry.content || "",
      mood: entry.mood || "😊",
    });

    setError("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // Cancel editing
  const cancelEdit = () => {
    setEditingId(null);
    setForm(getEmptyForm());
    setError("");
  };

  // Delete an entry
  const handleDelete = (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this journal entry?"
    );

    if (!confirmed) return;

    const updatedEntries = entries.filter(
      (entry) => String(entry.id) !== String(id)
    );

    if (saveEntries(updatedEntries)) {
      if (String(editingId) === String(id)) {
        cancelEdit();
      }
    }
  };

  return (
    <main style={styles.page}>
      <div style={styles.container}>

        {/* Back Button */}
        <button
          style={styles.back}
          onClick={() => navigate("/dreams")}
        >
          ← Back to Dashboard
        </button>

        {/* Page Heading */}
        <header style={styles.header}>
          <span style={styles.eyebrow}>
            REFLECT • LEARN • GROW
          </span>

          <h1>Your Learning Journal</h1>

          <p style={styles.muted}>
            Capture what you learn, celebrate small wins, and reflect
            on your journey towards your dreams.
          </p>
        </header>

        {/* Journal Form */}
        <section style={styles.formCard}>
          <h2>
            {editingId !== null
              ? "Edit Journal Entry ✏️"
              : "Add a Journal Entry"}
          </h2>

          <p style={styles.muted}>
            Write about your learning experience today.
          </p>

          <form onSubmit={handleSubmit}>

            <label style={styles.label} htmlFor="title">
              Entry Title
            </label>

            <input
              id="title"
              style={styles.input}
              name="title"
              placeholder="Example: Learned React basics"
              value={form.title}
              onChange={handleChange}
              required
            />

            <div style={styles.twoColumns}>
              <div>
                <label style={styles.label} htmlFor="date">
                  Date
                </label>

                <input
                  id="date"
                  style={styles.input}
                  type="date"
                  name="date"
                  value={form.date}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label style={styles.label} htmlFor="category">
                  Category
                </label>

                <select
                  id="category"
                  style={styles.input}
                  name="category"
                  value={form.category}
                  onChange={handleChange}
                >
                  <option>Learning</option>
                  <option>Practice</option>
                  <option>Project</option>
                  <option>Achievement</option>
                  <option>Reflection</option>
                </select>
              </div>
            </div>

            <label style={styles.label} htmlFor="mood">
              How are you feeling?
            </label>

            <select
              id="mood"
              style={styles.input}
              name="mood"
              value={form.mood}
              onChange={handleChange}
            >
              <option value="😊">😊 Happy</option>
              <option value="😃">😃 Excited</option>
              <option value="😐">😐 Okay</option>
              <option value="😓">😓 Challenged</option>
              <option value="💪">💪 Motivated</option>
            </select>

            <label style={styles.label} htmlFor="content">
              What did you learn today?
            </label>

            <textarea
              id="content"
              style={styles.textarea}
              name="content"
              placeholder="Describe what you studied, practiced, or achieved..."
              value={form.content}
              onChange={handleChange}
              rows="5"
              required
            />

            {error && (
              <p role="alert" style={styles.error}>
                {error}
              </p>
            )}

            <div style={styles.formActions}>
              <button type="submit" style={styles.submit}>
                {editingId !== null
                  ? "Update Journal Entry ✓"
                  : "+ Save Journal Entry"}
              </button>

              {editingId !== null && (
                <button
                  type="button"
                  style={styles.cancel}
                  onClick={cancelEdit}
                >
                  Cancel Editing
                </button>
              )}
            </div>
          </form>
        </section>

        {/* Journal Entries */}
        <section style={styles.entriesSection}>
          <div style={styles.entriesHeading}>
            <div>
              <h2>Your Entries</h2>
              <p style={styles.muted}>
                Your learning memories in one place.
              </p>
            </div>

            <span style={styles.count}>
              {entries.length} entries
            </span>
          </div>

          {entries.length === 0 ? (
            <div style={styles.empty}>
              <div style={{ fontSize: "42px" }}>📖</div>
              <h3>Your journal is waiting!</h3>
              <p style={styles.muted}>
                Add your first entry to begin tracking your learning.
              </p>
            </div>
          ) : (
            <div style={styles.entryList}>
              {entries.map((entry) => (
                <article
                  key={entry.id}
                  style={styles.entryCard}
                >
                  <div style={styles.entryTop}>
                    <div>
                      <span style={styles.category}>
                        {entry.category}
                      </span>

                      <h3 style={styles.entryTitle}>
                        {entry.title}
                      </h3>
                    </div>

                    <span style={{ fontSize: "25px" }}>
                      {entry.mood}
                    </span>
                  </div>

                  <p style={styles.entryContent}>
                    {entry.content}
                  </p>

                  <div style={styles.entryBottom}>
                    <span>📅 {entry.date}</span>

                    <div style={styles.entryActions}>
                      <button
                        style={styles.edit}
                        onClick={() => handleEdit(entry)}
                      >
                        ✏️ Edit
                      </button>

                      <button
                        style={styles.delete}
                        onClick={() => handleDelete(entry.id)}
                      >
                        🗑 Delete
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <p style={styles.footer}>
          Every day is an opportunity to learn something new. 💜
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
    maxWidth: "850px",
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
    marginBottom: "30px",
  },
  eyebrow: {
    color: "#6558d3",
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "2px",
  },
  formCard: {
    background: "white",
    padding: "28px",
    borderRadius: "18px",
    border: "1px solid #ececf4",
    marginBottom: "35px",
    boxShadow: "0 5px 18px rgba(50,40,100,0.04)",
  },
  label: {
    display: "block",
    fontSize: "13px",
    fontWeight: "600",
    color: "#45465b",
    margin: "18px 0 8px",
  },
  input: {
    width: "100%",
    padding: "12px",
    border: "1px solid #dedee9",
    borderRadius: "9px",
    fontSize: "14px",
    background: "white",
    boxSizing: "border-box",
  },
  textarea: {
    width: "100%",
    padding: "12px",
    border: "1px solid #dedee9",
    borderRadius: "9px",
    fontSize: "14px",
    resize: "vertical",
    boxSizing: "border-box",
    fontFamily: "inherit",
  },
  twoColumns: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: "18px",
  },
  formActions: {
    display: "flex",
    flexWrap: "wrap",
    gap: "12px",
    marginTop: "22px",
  },
  submit: {
    flex: 1,
    minWidth: "180px",
    padding: "13px",
    border: "none",
    borderRadius: "9px",
    background: "#6558d3",
    color: "white",
    fontWeight: "600",
    cursor: "pointer",
  },
  cancel: {
    padding: "13px 18px",
    border: "1px solid #dedee9",
    borderRadius: "9px",
    background: "white",
    color: "#6558d3",
    fontWeight: "600",
    cursor: "pointer",
  },
  error: {
    color: "#d9364f",
    fontSize: "13px",
    marginTop: "15px",
  },
  muted: {
    color: "#85869a",
    fontSize: "13px",
    lineHeight: 1.6,
  },
  entriesSection: {
    marginBottom: "30px",
  },
  entriesHeading: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    marginBottom: "18px",
  },
  count: {
    background: "#eeedff",
    color: "#6558d3",
    padding: "8px 13px",
    borderRadius: "20px",
    fontSize: "12px",
    fontWeight: "600",
    whiteSpace: "nowrap",
  },
  empty: {
    textAlign: "center",
    background: "white",
    padding: "45px 20px",
    borderRadius: "15px",
    border: "1px solid #ececf4",
  },
  entryList: {
    display: "grid",
    gap: "15px",
  },
  entryCard: {
    background: "white",
    padding: "22px",
    borderRadius: "16px",
    border: "1px solid #ececf4",
    boxShadow: "0 4px 15px rgba(50,40,100,0.04)",
  },
  entryTop: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
  },
  category: {
    color: "#6558d3",
    fontSize: "11px",
    fontWeight: "700",
    textTransform: "uppercase",
  },
  entryTitle: {
    color: "#30284f",
    margin: "8px 0",
    overflowWrap: "anywhere",
  },
  entryContent: {
    color: "#65667a",
    fontSize: "14px",
    lineHeight: 1.7,
    whiteSpace: "pre-wrap",
  },
  entryBottom: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "12px",
    color: "#85869a",
    fontSize: "12px",
    borderTop: "1px solid #eeeeF5",
    paddingTop: "13px",
  },
  entryActions: {
    display: "flex",
    gap: "15px",
  },
  edit: {
    border: "none",
    background: "transparent",
    color: "#6558d3",
    cursor: "pointer",
    fontWeight: "600",
  },
  delete: {
    border: "none",
    background: "transparent",
    color: "#d95365",
    cursor: "pointer",
    fontWeight: "600",
  },
  footer: {
    textAlign: "center",
    color: "#85869a",
    fontSize: "13px",
    marginTop: "30px",
  },
};

export default JournalPage;
