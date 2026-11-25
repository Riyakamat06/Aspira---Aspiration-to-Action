
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Journal.css';

function Journal() {
  const [entries, setEntries] = useState([
    {
      id: 1,
      title: 'My First Learning Goal',
      content: 'Started learning HTML and CSS. Practiced creating webpages and designing layouts.',
      category: 'Learning',
      date: '2026-11-15',
    },
    {
      id: 2,
      title: 'JavaScript Practice',
      content: 'Learned variables, functions and basic JavaScript concepts.',
      category: 'Achievement',
      date: '2026-11-16',
    },
  ]);

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('Learning');

  const addEntry = (e) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) {
      alert('Please fill in all fields.');
      return;
    }

    const newEntry = {
      id: Date.now(),
      title: title.trim(),
      content: content.trim(),
      category,
      date: new Date().toISOString().split('T')[0],
    };

    setEntries((current) => [newEntry, ...current]);

    setTitle('');
    setContent('');
    setCategory('Learning');
  };

  const deleteEntry = (id) => {
    setEntries((current) =>
      current.filter((entry) => entry.id !== id)
    );
  };

  return (
    <main className="journal-page">

      <Link to="/" className="journal-back">
        ← Dashboard
      </Link>

      <header className="journal-header">
        <div>
          <span className="journal-eyebrow">
            YOUR PERSONAL SPACE
          </span>

          <h1>Learning Journal</h1>

          <p>
            Reflect on your journey, celebrate achievements
            and learn from every experience.
          </p>
        </div>

        <div className="journal-icon">📖</div>
      </header>

      <section className="journal-welcome">
        <div>
          <h2>Every small step counts! ✨</h2>
          <p>
            Your dreams become reality through consistent
            learning and progress.
          </p>
        </div>
      </section>

      <section className="journal-layout">

        <article className="journal-form-panel">
          <h2>Write a New Entry</h2>

          <p>Capture your thoughts and experiences.</p>

          <form onSubmit={addEntry}>

            <label>Entry Title</label>

            <input
              type="text"
              placeholder="What did you learn today?"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />

            <label>Category</label>

            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="Learning">Learning</option>
              <option value="Achievement">Achievement</option>
              <option value="Challenge">Challenge</option>
              <option value="Reflection">Reflection</option>
            </select>

            <label>Your Experience</label>

            <textarea
              rows="6"
              placeholder="Write about your learning experience..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />

            <button type="submit">
              + Save Journal Entry
            </button>

          </form>
        </article>

        <article className="journal-entries-panel">

          <div className="journal-entries-heading">
            <div>
              <h2>My Journal Entries</h2>
              <p>Your learning memories and achievements.</p>
            </div>

            <span>{entries.length} Entries</span>
          </div>

          {entries.length === 0 ? (
            <div className="journal-empty">
              <span>📝</span>
              <h3>No entries yet</h3>
              <p>Start writing your first learning experience!</p>
            </div>
          ) : (

            <div className="journal-entry-list">

              {entries.map((entry) => (

                <div className="journal-entry" key={entry.id}>

                  <div className="entry-top">
                    <span className="entry-category">
                      {entry.category}
                    </span>

                    <span className="entry-date">
                      {entry.date}
                    </span>
                  </div>

                  <h3>{entry.title}</h3>

                  <p>{entry.content}</p>

                  <button
                    className="delete-entry"
                    onClick={() => deleteEntry(entry.id)}
                  >
                    Delete Entry
                  </button>

                </div>

              ))}

            </div>
          )}

        </article>

      </section>

    </main>
  );
}

export default Journal;
