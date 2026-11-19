
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function AnalyticsPage() {
  const navigate = useNavigate();

  const [dreams, setDreams] = useState([]);
  const [entries, setEntries] = useState([]);

  // Load saved data
  useEffect(() => {
    try {
      const savedDreams = JSON.parse(
        localStorage.getItem("aspiraDreams") || "[]"
      );

      const savedEntries = JSON.parse(
        localStorage.getItem("aspiraJournal") || "[]"
      );

      setDreams(Array.isArray(savedDreams) ? savedDreams : []);
      setEntries(Array.isArray(savedEntries) ? savedEntries : []);
    } catch (error) {
      console.error("Analytics loading error:", error);
      setDreams([]);
      setEntries([]);
    }
  }, []);

  // Calculate task statistics
  const allTasks = dreams.flatMap((dream) =>
    (Array.isArray(dream.roadmapTasks) ? dream.roadmapTasks : [])
      .flatMap((phase) =>
        Array.isArray(phase.tasks) ? phase.tasks : []
      )
  );

  const completedTasks = allTasks.filter(
    (task) => typeof task === "object" && task.completed
  ).length;

  const totalTasks = allTasks.length;
  const pendingTasks = totalTasks - completedTasks;

  const overallProgress = totalTasks === 0
    ? 0
    : Math.round((completedTasks / totalTasks) * 100);

  // Calculate career categories
  const categories = dreams.reduce((result, dream) => {
    const category = dream.category || "Other";
    result[category] = (result[category] || 0) + 1;
    return result;
  }, {});

  const careerAreas = Object.keys(categories).length;

  // Weekly journal activity
  const weeklyData = Array.from({ length: 7 }, (_, index) => {
    const date = new Date();
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() - (6 - index));

    const dateString = [
      date.getFullYear(),
      String(date.getMonth() + 1).padStart(2, "0"),
      String(date.getDate()).padStart(2, "0"),
    ].join("-");

    return {
      day: date.toLocaleDateString("en-US", {
        weekday: "short",
      }),
      date: dateString,
      count: entries.filter(
        (entry) => entry.date === dateString
      ).length,
    };
  });

  const maxCount = Math.max(
    1,
    ...weeklyData.map((day) => day.count)
  );

  const weeklyTotal = weeklyData.reduce(
    (total, day) => total + day.count,
    0
  );

  // Calculate individual roadmap progress
  const dreamProgress = dreams.map((dream) => {
    const phases = Array.isArray(dream.roadmapTasks)
      ? dream.roadmapTasks
      : [];

    const tasks = phases.flatMap((phase) =>
      Array.isArray(phase.tasks) ? phase.tasks : []
    );

    const completed = tasks.filter(
      (task) => typeof task === "object" && task.completed
    ).length;

    const total = tasks.length;

    return {
      id: dream.id,
      title: dream.title || "Untitled Dream",
      category: dream.category || "Other",
      completed,
      total,
      progress: total === 0
        ? 0
        : Math.round((completed / total) * 100),
    };
  });

  // Overall statistics
  const stats = [
    {
      icon: "🎯",
      value: dreams.length,
      label: "Total Dreams",
      color: "#6558d3",
    },
    {
      icon: "✅",
      value: completedTasks,
      label: "Tasks Completed",
      color: "#239568",
    },
    {
      icon: "⏳",
      value: pendingTasks,
      label: "Pending Tasks",
      color: "#d99a36",
    },
    {
      icon: "📖",
      value: entries.length,
      label: "Journal Entries",
      color: "#4385c5",
    },
  ];

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
            YOUR GROWTH AT A GLANCE
          </span>

          <h1>Progress Analytics</h1>

          <p style={styles.subtitle}>
            Understand your learning habits, track your achievements,
            and see how far you have come.
          </p>
        </header>

        {/* Statistics Cards */}
        <section style={styles.statsGrid}>
          {stats.map((stat) => (
            <div style={styles.statCard} key={stat.label}>
              <span style={styles.statIcon}>
                {stat.icon}
              </span>

              <h2 style={{ color: stat.color }}>
                {stat.value}
              </h2>

              <p>{stat.label}</p>
            </div>
          ))}
        </section>

        {/* Overall Progress */}
        <section style={styles.chartCard}>
          <div style={styles.cardHeading}>
            <div>
              <h2>Overall Learning Progress</h2>
              <p style={styles.muted}>
                Your progress across all your roadmaps.
              </p>
            </div>

            <strong style={styles.percentage}>
              {overallProgress}%
            </strong>
          </div>

          <div style={styles.progressTrack}>
            <div
              style={{
                ...styles.progressFill,
                width: `${overallProgress}%`,
              }}
            />
          </div>

          <div style={styles.progressDetails}>
            <span>
              {completedTasks} completed
            </span>

            <span>
              {pendingTasks} remaining
            </span>
          </div>
        </section>

        {/* Weekly Activity Chart */}
        <section style={styles.chartCard}>
          <div style={styles.cardHeading}>
            <div>
              <h2>Weekly Learning Activity</h2>

              <p style={styles.muted}>
                Journal entries recorded during the last 7 days.
              </p>
            </div>

            <span style={styles.badge}>
              {weeklyTotal} entries
            </span>
          </div>

          <div style={styles.chart}>
            {weeklyData.map((day) => (
              <div style={styles.barColumn} key={day.date}>
                <span style={styles.barValue}>
                  {day.count || ""}
                </span>

                <div style={styles.barArea}>
                  <div
                    style={{
                      ...styles.bar,
                      height: `${
                        day.count > 0
                          ? Math.max(
                              10,
                              (day.count / maxCount) * 100
                            )
                          : 3
                      }%`,
                      opacity: day.count > 0 ? 1 : 0.2,
                    }}
                  />
                </div>

                <span style={styles.dayLabel}>
                  {day.day}
                </span>
              </div>
            ))}
          </div>

          <p style={styles.chartNote}>
            Each bar represents the number of journal entries
            recorded on that day.
          </p>
        </section>

        {/* Individual Roadmap Progress */}
        <section style={styles.chartCard}>
          <div style={styles.cardHeading}>
            <div>
              <h2>My Roadmap Progress</h2>

              <p style={styles.muted}>
                Track the progress of each dream separately.
              </p>
            </div>
          </div>

          {dreamProgress.length === 0 ? (
            <p style={styles.empty}>
              You haven't created any dreams yet.
            </p>
          ) : (
            <div style={styles.roadmapList}>
              {dreamProgress.map((dream) => (
                <div
                  style={styles.roadmapItem}
                  key={dream.id}
                >
                  <div style={styles.roadmapHeading}>
                    <div>
                      <h3>{dream.title}</h3>

                      <span style={styles.category}>
                        {dream.category}
                      </span>
                    </div>

                    <strong style={styles.roadmapPercentage}>
                      {dream.progress}%
                    </strong>
                  </div>

                  <div style={styles.progressTrack}>
                    <div
                      style={{
                        ...styles.progressFill,
                        width: `${dream.progress}%`,
                      }}
                    />
                  </div>

                  <p style={styles.roadmapText}>
                    {dream.completed} of {dream.total} tasks completed
                  </p>

                  <button
                    style={styles.viewButton}
                    onClick={() =>
                      navigate(`/roadmap/${dream.id}`)
                    }
                  >
                    View Roadmap →
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Career Area Distribution */}
        <section style={styles.chartCard}>
          <div style={styles.cardHeading}>
            <div>
              <h2>Dreams by Career Area</h2>

              <p style={styles.muted}>
                Explore how your aspirations are distributed.
              </p>
            </div>
          </div>

          {Object.keys(categories).length === 0 ? (
            <p style={styles.empty}>
              Add a dream to see your career-area statistics.
            </p>
          ) : (
            <div style={styles.categoryList}>
              {Object.entries(categories).map(
                ([category, count]) => {
                  const percentage = Math.round(
                    (count / dreams.length) * 100
                  );

                  return (
                    <div key={category}>
                      <div style={styles.categoryHeading}>
                        <span>{category}</span>
                        <strong>
                          {count} ({percentage}%)
                        </strong>
                      </div>

                      <div style={styles.categoryTrack}>
                        <div
                          style={{
                            ...styles.categoryFill,
                            width: `${percentage}%`,
                          }}
                        />
                      </div>
                    </div>
                  );
                }
              )}
            </div>
          )}
        </section>

        {/* Insights */}
        <section style={styles.insightCard}>
          <span style={{ fontSize: "28px" }}>💡</span>

          <div>
            <h3>Your Learning Insight</h3>

            <p>
              {totalTasks === 0
                ? "Start a dream and create your roadmap to begin tracking your learning progress."
                : overallProgress === 100
                ? "Amazing work! You have completed all your current roadmap tasks. Keep setting new goals!"
                : `You have completed ${overallProgress}% of your roadmap tasks. Keep learning and take one step closer to your dreams!`}
            </p>

            <p style={styles.insightExtra}>
              You have recorded {entries.length} journal entries
              and explored {careerAreas} career area(s).
            </p>
          </div>
        </section>

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
    maxWidth: "1000px",
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
  subtitle: {
    color: "#85869a",
    fontSize: "14px",
    lineHeight: 1.7,
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "16px",
    marginBottom: "25px",
  },
  statCard: {
    background: "white",
    border: "1px solid #ececf4",
    borderRadius: "16px",
    padding: "22px",
    boxShadow: "0 5px 18px rgba(50,40,100,0.04)",
  },
  statIcon: {
    fontSize: "25px",
  },
  chartCard: {
    background: "white",
    border: "1px solid #ececf4",
    borderRadius: "17px",
    padding: "25px",
    marginBottom: "22px",
    boxShadow: "0 5px 18px rgba(50,40,100,0.04)",
  },
  cardHeading: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "12px",
    marginBottom: "25px",
  },
  muted: {
    color: "#85869a",
    fontSize: "13px",
    lineHeight: 1.6,
  },
  percentage: {
    color: "#6558d3",
    fontSize: "27px",
  },
  progressTrack: {
    height: "10px",
    background: "#eeeeF7",
    borderRadius: "20px",
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    background: "linear-gradient(90deg, #8e80ed, #5144bd)",
    borderRadius: "20px",
    transition: "width 0.3s ease",
  },
  progressDetails: {
    display: "flex",
    justifyContent: "space-between",
    marginTop: "12px",
    color: "#85869a",
    fontSize: "12px",
  },
  badge: {
    background: "#f0efff",
    color: "#6558d3",
    padding: "7px 12px",
    borderRadius: "20px",
    fontSize: "12px",
  },
  chart: {
    height: "210px",
    display: "flex",
    alignItems: "stretch",
    justifyContent: "space-around",
    gap: "12px",
    borderBottom: "1px solid #eeeeF5",
  },
  barColumn: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "7px",
    minWidth: 0,
  },
  barValue: {
    fontSize: "12px",
    color: "#6558d3",
    fontWeight: "600",
    height: "15px",
  },
  barArea: {
    flex: 1,
    width: "100%",
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "center",
  },
  bar: {
    width: "55%",
    maxWidth: "45px",
    minHeight: "3px",
    background: "linear-gradient(180deg, #887ce9, #6558d3)",
    borderRadius: "7px 7px 0 0",
    transition: "height 0.3s ease",
  },
  dayLabel: {
    color: "#85869a",
    fontSize: "12px",
    marginBottom: "7px",
  },
  chartNote: {
    color: "#85869a",
    fontSize: "12px",
    marginTop: "15px",
  },
  roadmapList: {
    display: "grid",
    gap: "22px",
  },
  roadmapItem: {
    background: "#faf9ff",
    padding: "18px",
    borderRadius: "13px",
    border: "1px solid #f0edfa",
  },
  roadmapHeading: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    marginBottom: "15px",
  },
  category: {
    color: "#85869a",
    fontSize: "12px",
  },
  roadmapPercentage: {
    color: "#6558d3",
    fontSize: "19px",
  },
  roadmapText: {
    color: "#85869a",
    fontSize: "12px",
  },
  viewButton: {
    border: "none",
    background: "transparent",
    color: "#6558d3",
    fontSize: "12px",
    fontWeight: "600",
    cursor: "pointer",
    padding: "5px 0",
  },
  categoryList: {
    display: "grid",
    gap: "20px",
  },
  categoryHeading: {
    display: "flex",
    justifyContent: "space-between",
    color: "#55566b",
    fontSize: "13px",
    marginBottom: "8px",
  },
  categoryTrack: {
    height: "9px",
    background: "#eeeeF7",
    borderRadius: "20px",
    overflow: "hidden",
  },
  categoryFill: {
    height: "100%",
    background: "linear-gradient(90deg, #887ce9, #6558d3)",
    borderRadius: "20px",
  },
  empty: {
    color: "#85869a",
    fontSize: "14px",
    padding: "15px 0",
  },
  insightCard: {
    display: "flex",
    alignItems: "flex-start",
    gap: "16px",
    background: "#eeedff",
    borderRadius: "16px",
    padding: "22px",
    marginTop: "25px",
    color: "#454078",
  },
  insightExtra: {
    fontSize: "12px",
    color: "#77719f",
  },
};

export default AnalyticsPage;
