
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Roadmaps.css';

function Roadmaps() {
  const [showForm, setShowForm] = useState(false);
  const [dream, setDream] = useState('');
  const [category, setCategory] = useState('Technology');
  const [dreams, setDreams] = useState([
    { id: 1, title: 'Full Stack Developer', category: 'Technology', progress: 72 },
    { id: 2, title: 'UI/UX Designer', category: 'Creative', progress: 45 },
    { id: 3, title: 'Data Analyst', category: 'Technology', progress: 28 },
  ]);

  const createRoadmap = (e) => {
    e.preventDefault();

    if (!dream.trim()) return;

    setDreams([
      ...dreams,
      {
        id: Date.now(),
        title: dream.trim(),
        category,
        progress: 0,
      },
    ]);

    setDream('');
    setShowForm(false);
  };

  const deleteRoadmap = (id) => {
    setDreams(dreams.filter((item) => item.id !== id));
  };

  return (
    <div className="roadmaps-page">
      <header className="roadmaps-header">
        <div>
          <Link to="/" className="back-link">← Dashboard</Link>
          <p className="page-label">YOUR CAREER JOURNEY</p>
          <h1>My Roadmaps</h1>
          <p className="page-description">
            Every dream deserves a plan. Organise your goals and turn them into action.
          </p>
        </div>

        <button className="create-btn" onClick={() => setShowForm(!showForm)}>
          + Create New Dream
        </button>
      </header>

      {showForm && (
        <section className="create-form-card">
          <h2>Create a new dream</h2>
          <p>Tell ASPIRA what you want to achieve.</p>

          <form onSubmit={createRoadmap}>
            <label htmlFor="dream">Your career goal</label>
            <input
              id="dream"
              type="text"
              placeholder="Example: Become a Software Engineer"
              value={dream}
              onChange={(e) => setDream(e.target.value)}
              required
            />

            <label htmlFor="category">Career category</label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option>Technology</option>
              <option>Creative</option>
              <option>Business</option>
              <option>Healthcare</option>
              <option>Education</option>
              <option>Arts and Entertainment</option>
              <option>Other</option>
            </select>

            <div className="form-actions">
              <button type="button" className="cancel-btn" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button type="submit" className="create-btn">
                Create Dream
              </button>
            </div>
          </form>
        </section>
      )}

      <div className="roadmap-summary">
        <div>
          <span>Total dreams</span>
          <strong>{dreams.length}</strong>
        </div>
        <div>
          <span>In progress</span>
          <strong>{dreams.filter((item) => item.progress > 0).length}</strong>
        </div>
        <div>
          <span>Just started</span>
          <strong>{dreams.filter((item) => item.progress === 0).length}</strong>
        </div>
      </div>

      <section className="my-dreams-section">
        <div className="my-dreams-heading">
          <div>
            <h2>Your dreams</h2>
            <p>Keep track of every career path you're exploring.</p>
          </div>
        </div>

        {dreams.length === 0 ? (
          <div className="empty-state">
            <div>✧</div>
            <h3>Your next chapter starts here</h3>
            <p>Create your first dream and begin building your roadmap.</p>
            <button className="create-btn" onClick={() => setShowForm(true)}>
              + Create your first dream
            </button>
          </div>
        ) : (
          <div className="dreams-grid">
            {dreams.map((item) => (
              <article className="dream-card" key={item.id}>
                <div className="dream-card-top">
                  <span className="dream-icon">✦</span>
                  <button
                    className="delete-btn"
                    onClick={() => deleteRoadmap(item.id)}
                    aria-label={`Delete ${item.title}`}
                  >
                    Delete
                  </button>
                </div>

                <span className="dream-category">{item.category}</span>
                <h3>{item.title}</h3>

                <div className="dream-progress-label">
                  <span>Current progress</span>
                  <strong>{item.progress}%</strong>
                </div>

                <div className="dream-progress-track">
                  <div
                    className="dream-progress-fill"
                    style={{ width: `${item.progress}%` }}
                  ></div>
                </div>

                <p className="dream-status">
                  {item.progress === 0 ? 'Ready to begin' : 'Journey in progress'}
                </p>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Roadmaps;
