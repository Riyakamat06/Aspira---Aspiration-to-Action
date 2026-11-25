
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

function DreamListPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [dreams, setDreams] = useState([]);

  // Load saved dreams when the dashboard opens
  useEffect(() => {
    try {
      const savedDreams = JSON.parse(
        localStorage.getItem("aspiraDreams") || "[]"
      );

      setDreams(Array.isArray(savedDreams) ? savedDreams : []);
    } catch {
      setDreams([]);
    }
  }, []);

  // Count completed tasks across all dreams
  const completedTasks = dreams.reduce((total, dream) => {
    const phases = Array.isArray(dream.roadmapTasks)
      ? dream.roadmapTasks
      : [];

    const completed = phases.reduce((count, phase) => {
      const tasks = Array.isArray(phase.tasks) ? phase.tasks : [];

      return (
        count +
        tasks.filter(
          (task) => typeof task === "object" && task.completed
        ).length
      );
    }, 0);

    return total + completed;
  }, 0);

  // Delete a dream
  const handleDelete = (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this dream?"
    );

    if (!confirmed) return;

    const updatedDreams = dreams.filter(
      (dream) => dream.id !== id
    );

    setDreams(updatedDreams);

    localStorage.setItem(
      "aspiraDreams",
      JSON.stringify(updatedDreams)
    );
  };

  // Calculate progress for an individual dream
  const getDreamProgress = (dream) => {
    const phases = Array.isArray(dream.roadmapTasks)
      ? dream.roadmapTasks
      : [];

    const tasks = phases.flatMap((phase) =>
      Array.isArray(phase.tasks) ? phase.tasks : []
    );

    if (tasks.length === 0) return 0;

    const completed = tasks.filter(
      (task) => typeof task === "object" && task.completed
    ).length;

    return Math.round((completed / tasks.length) * 100);
  };

  const userName = user?.name || "Achiever";

  const careerAreas = new Set(
    dreams
      .map((dream) => dream.category)
      .filter(Boolean)
  ).size;

  const roadmapsStarted = dreams.filter(
    (dream) =>
      Array.isArray(dream.roadmapTasks) &&
      dream.roadmapTasks.length > 0
  ).length;

  return (
    <div className="dashboard-layout">
      <main className="dashboard-main">

        {/* Dashboard Header */}
        <header className="dashboard-header">
          <div>
            <p style={{ color: "#6558d3", fontWeight: "600" }}>
              YOUR ASPIRA JOURNEY
            </p>

            <h1>Dashboard</h1>

            <p>
              Welcome back, {userName}! Keep moving towards your dreams.
            </p>
          </div>

          <button onClick={() => navigate("/intake")}>
            + Add New Dream
          </button>
        </header>

        {/* Welcome Section */}
        <section className="welcome-card">
          <div>
            <h2>Your dreams deserve a plan.</h2>

            <p>
              Turn your aspirations into achievable goals with
              your personalized learning journey.
            </p>

            <button onClick={() => navigate("/intake")}>
              Start a New Journey →
            </button>
          </div>

          <span style={{ fontSize: "65px" }}>🚀</span>
        </section>

        {/* Statistics */}
        <section className="stats-grid">

          <div className="stat-card">
            <h3>{dreams.length}</h3>
            <p>Total Dreams</p>
            <span>✨ Your aspirations</span>
          </div>

          <div className="stat-card">
            <h3>{careerAreas}</h3>
            <p>Career Areas</p>
            <span>🎯 Your interests</span>
          </div>

          <div className="stat-card">
            <h3>{roadmapsStarted}</h3>
            <p>Roadmaps Started</p>
            <span>🗺️ Your learning plans</span>
          </div>

          <div className="stat-card">
            <h3>{completedTasks}</h3>
            <p>Tasks Completed</p>
            <span>🏆 Your achievements</span>
          </div>

        </section>

        {/* Dreams Section */}
        <section className="dreams-section">

          <div className="section-heading">
            <div>
              <h2>My Dreams ✨</h2>

              <p>
                Your aspirations and learning journeys in one place.
              </p>
            </div>
          </div>

          {dreams.length === 0 ? (

            /* Empty State */
            <div className="empty-state">
              <div style={{ fontSize: "55px" }}>🌱</div>

              <h3>Your journey starts here!</h3>

              <p>
                You haven't added any dreams yet.
                Create your first dream and let ASPIRA
                help you achieve it.
              </p>

              <button onClick={() => navigate("/intake")}>
                + Add Your First Dream
              </button>
            </div>

          ) : (

            /* Dream Cards */
            <div className="dream-cards">

              {dreams.map((dream) => {
                const progress = getDreamProgress(dream);

                return (
                  <article className="dream-card" key={dream.id}>

                    <span className="dream-category">
                      {dream.category || "Personal Goal"}
                    </span>

                    <h3>{dream.title || "Untitled Dream"}</h3>

                    <p>
                      {dream.description ||
                        "Your journey towards achieving this dream begins here."}
                    </p>

                    <div className="dream-info">
                      <span>
                        📚 {dream.currentLevel || "Not specified"}
                      </span>

                      <span>
                        📅 {dream.timeline || "Flexible"}
                      </span>

                      <span>
                        ⏰ {dream.hours || 0} hours/day
                      </span>
                    </div>

                    {/* Progress */}
                    <div className="dream-progress">

                      <div className="progress-heading">
                        <span>Learning Progress</span>
                        <strong>{progress}%</strong>
                      </div>

                      <div className="progress-track">
                        <div
                          className="progress-fill"
                          style={{ width: `${progress}%` }}
                        />
                      </div>

                    </div>

                    {/* Actions */}
                    <div className="dream-actions">

                      <button
                        onClick={() =>
                          navigate(`/roadmap/${dream.id}`)
                        }
                      >
                        Open Roadmap →
                      </button>

                      <button
                        className="delete-btn"
                        onClick={() => handleDelete(dream.id)}
                      >
                        Delete
                      </button>

                    </div>

                  </article>
                );
              })}

            </div>
          )}

        </section>

      </main>
    </div>
  );
}

export default DreamListPage;
