
import React, { useState } from "react";
import "./JournalEditor.css";

function JournalEditor({ initialEntry = null, onSave, onCancel }) {
  const [title, setTitle] = useState(initialEntry?.title || "");
  const [content, setContent] = useState(initialEntry?.content || "");
  const [mood, setMood] = useState(initialEntry?.mood || "Good");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSave = async (e) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) {
      setError("Please enter both a title and journal entry.");
      return;
    }

    if (!onSave) {
      setError("Save action is not connected yet.");
      return;
    }

    try {
      setSaving(true);
      setError("");

      await onSave({
        title: title.trim(),
        content: content.trim(),
        mood,
      });
    } catch (err) {
      setError(err.message || "Unable to save your journal entry.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="journal-editor">
      <div className="journal-heading">
        <div>
          <span className="journal-label">YOUR PERSONAL SPACE</span>
          <h2>Learning Journal ✨</h2>
          <p>Reflect on your journey, celebrate progress, and keep growing.</p>
        </div>
        <span className="journal-icon">📖</span>
      </div>

      <form onSubmit={handleSave}>
        <div className="journal-field">
          <label htmlFor="journal-title">Entry Title</label>
          <input
            id="journal-title"
            type="text"
            placeholder="What did you learn today?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div className="journal-field">
          <label htmlFor="journal-mood">How are you feeling today?</label>
          <select
            id="journal-mood"
            value={mood}
            onChange={(e) => setMood(e.target.value)}
          >
            <option value="Amazing">😊 Amazing</option>
            <option value="Good">🙂 Good</option>
            <option value="Okay">😐 Okay</option>
            <option value="Tired">😴 Tired</option>
            <option value="Stressed">😟 Stressed</option>
          </select>
        </div>

        <div className="journal-field">
          <label htmlFor="journal-content">Your Reflection</label>
          <textarea
            id="journal-content"
            placeholder="Write about what you learned, challenges you faced, and what you want to improve..."
            rows="8"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <span className="journal-hint">
            Be honest with yourself. Every small step matters!
          </span>
        </div>

        {error && <p className="journal-error">{error}</p>}

        <div className="journal-actions">
          {onCancel && (
            <button
              type="button"
              className="journal-cancel"
              onClick={onCancel}
            >
              Cancel
            </button>
          )}

          <button
            type="submit"
            className="journal-save"
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Journal Entry"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default JournalEditor;
