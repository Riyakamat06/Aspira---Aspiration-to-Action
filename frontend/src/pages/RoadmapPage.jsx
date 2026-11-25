
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const defaultTasks = [
  {
    phase: "Phase 1",
    title: "Explore & Plan",
    duration: "Week 1",
    tasks: [
      "Understand your career goal",
      "Research required skills and qualifications",
      "Create a learning schedule",
    ],
  },
  {
    phase: "Phase 2",
    title: "Build Your Foundation",
    duration: "Weeks 2–4",
    tasks: [
      "Learn the fundamental concepts",
      "Study important topics",
      "Practice beginner-level exercises",
    ],
  },
  {
    phase: "Phase 3",
    title: "Practice & Build",
    duration: "Weeks 5–8",
    tasks: [
      "Work on practical exercises",
      "Complete a mini project",
      "Improve your skills through regular practice",
    ],
  },
  {
    phase: "Phase 4",
    title: "Prepare for Opportunities",
    duration: "Weeks 9–12",
    tasks: [
      "Build your portfolio or resume",
      "Complete a final project",
      "Prepare for interviews or applications",
    ],
  },
];

// Convert old string tasks into objects
function normalizeTasks(roadmapTasks) {
  const source = Array.isArray(roadmapTasks) && roadmapTasks.length
    ? roadmapTasks
    : defaultTasks;

  return source.map((phase, index) => ({
    ...phase,
    phase: phase.phase || `Phase ${index + 1}`,
    title: phase.title || `Learning Phase ${index + 1}`,
    duration: phase.duration || "Flexible",
    tasks: (Array.isArray(phase.tasks) ? phase.tasks : []).map((task) =>
      typeof task === "string"
        ? { title: task, completed: false }
        : {
            ...task,
            title: task.title || "Untitled task",
            completed: Boolean(task.completed),
          }
    ),
  }));
}

function RoadmapPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [dream, setDream] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");

  // Load selected dream
  useEffect(() => {
    try {
      const savedDreams = JSON.parse(
        localStorage.getItem("aspiraDreams") || "[]"
      );

      if (!Array.isArray(savedDreams)) {
        throw new Error("Invalid dream data");
      }

      const selectedDream = savedDreams.find(
        (item) => String(item.id) === String(id)
      );

      if (!selectedDream) {
        navigate("/dreams", { replace: true });
        return;
      }

      const normalizedTasks = normalizeTasks(
        selectedDream.roadmapTasks
      );

      setDream(selectedDream);
      setTasks(normalizedTasks);

      // Save the default roadmap if one does not exist
      if (
        !Array.isArray(selectedDream.roadmapTasks) ||
        selectedDream.roadmapTasks.length === 0
      ) {
        const updatedDreams = savedDreams.map((item) =>
          String(item.id) === String(id)
            ? { ...item, roadmapTasks: normalizedTasks }
            : item
        );

        localStorage.setItem(
          "aspiraDreams",
          JSON.stringify(updatedDreams)
        );
      }
    } catch (err) {
      console.error("Roadmap loading error:", err);
      setError("Unable to load your roadmap. Please try again.");
    }
  }, [id, navigate]);

  // Save updated tasks
  const saveTasks = (updatedTasks) => {
    try {
      const savedDreams = JSON.parse(
        localStorage.getItem("aspiraDreams") || "[]"
      );

      if (!Array.isArray(savedDreams)) {
        throw new Error("Invalid dream data");
      }

      const updatedDreams = savedDreams.map((item) =>
        String(item.id) === String(id)
          ? { ...item, roadmapTasks: updatedTasks }
          : item
      );

      localStorage.setItem(
        "aspiraDreams",
        JSON.stringify(updatedDreams)
      );

      setTasks(updatedTasks);
    } catch (err) {
      console.error("Task saving error:", err);
      setError("Unable to save your progress. Please try again.");
    }
  };

  // Check or uncheck a task
  const updateTask = (phaseIndex, taskIndex) => {
    const updatedTasks = tasks.map((phase, pIndex) => {
      if (pIndex !== phaseIndex) return phase;

      return {
        ...phase,
        tasks: phase.tasks.map((task, tIndex) => {
          if (tIndex !== taskIndex) return task;

          return {
            ...task,
            completed: !task.completed,
          };
        }),
      };
    });

    setError("");
    saveTasks(updatedTasks);
  };

  if (error && !dream) {
    return (
      <main style={styles.page}>
        <div style={styles.errorCard}>
          <h2>Something went wrong</h2>
          <p>{error}</p>
          <button
            style={styles.primaryButton}
            onClick={() => navigate("/dreams")}
          >
            Back to Dashboard
          </button>
        </div>
      </main>
    );
  }

  if (!dream) return null;

  // Calculate overall progress
  const allTasks = tasks.flatMap((phase) => phase.tasks);

  const completedTasks = allTasks.filter(
    (task) => task.completed
  ).length;

  const totalTasks = allTasks.length;

  const progress = totalTasks === 0
    ? 0
    : Math.round((completedTasks / totalTasks) * 100);

  return (
    <main style={styles.page}>
      <div style={styles.container}>

        {/* Back Button */}
        <button
          onClick={() => navigate("/dreams")}
          style={styles.backButton}
        >
          ← Back to Dashboard
        </button>

        {/* Hero Section */}
        <section style={styles.hero}>
          <span style={styles.tag}>YOUR PERSONAL ROADMAP</span>

          <h1 style={styles.heading}>{dream.title}</h1>

          <p style={styles.description}>
            Your journey starts here. Follow each phase, complete your
            tasks, and make consistent progress towards your aspiration.
          </p>

          <div style={styles.details}>
            <span>🎯 {dream.category}</span>
            <span>📅 {dream.timeline}</span>
            <span>⏰ {dream.hours} per day</span>
          </div>
        </section>

        {/* Overall Progress */}
        <section style={styles.progressCard}>
          <div style={styles.progressHeader}>
            <div>
              <h2 style={styles.sectionTitle}>Your Progress</h2>
              <p style={styles.muted}>
                Keep going! Every completed task brings you closer.
              </p>
            </div>

            <strong style={styles.percentage}>
              {progress}%
            </strong>
          </div>

          <div style={styles.progressTrack}>
            <div
              style={{
                ...styles.progressFill,
                width: `${progress}%`,
              }}
            />
          </div>

          <p style={styles.progressText}>
            {completedTasks} of {totalTasks} tasks completed
          </p>

          {progress === 100 && totalTasks > 0 && (
            <p style={styles.successMessage}>
              🎉 Congratulations! You completed your roadmap!
            </p>
          )}
        </section>

        {/* Learning Journey */}
        <div style={styles.roadmapHeading}>
          <div>
            <h2 style={styles.sectionTitle}>
              Your Learning Journey
            </h2>

            <p style={styles.muted}>
              Complete the activities in each phase at your own pace.
            </p>
          </div>
        </div>

        {/* Roadmap Phases */}
        <div style={styles.phases}>
          {tasks.map((phase, phaseIndex) => {
            const phaseCompleted = phase.tasks.filter(
              (task) => task.completed
            ).length;

            const phaseTotal = phase.tasks.length;

            const phaseProgress = phaseTotal === 0
              ? 0
              : Math.round((phaseCompleted / phaseTotal) * 100);

            return (
              <section style={styles.phaseCard} key={phase.phase}>
                <div style={styles.phaseHeader}>
                  <div>
                    <span style={styles.phaseTag}>
                      {phase.phase}
                    </span>

                    <h3 style={styles.phaseTitle}>
                      {phase.title}
                    </h3>
                  </div>

                  <span style={styles.duration}>
                    {phase.duration}
                  </span>
                </div>

                {/* Phase Progress */}
                <div style={styles.phaseProgress}>
                  <div style={styles.phaseProgressHeader}>
                    <span>Phase progress</span>
                    <strong>{phaseProgress}%</strong>
                  </div>

                  <div style={styles.smallProgressTrack}>
                    <div
                      style={{
                        ...styles.smallProgressFill,
                        width: `${phaseProgress}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Tasks */}
                <div style={styles.taskList}>
                  {phase.tasks.map((task, taskIndex) => (
                    <label
                      style={styles.task}
                      key={taskIndex}
                    >
                      <input
                        type="checkbox"
                        checked={task.completed}
                        onChange={() =>
                          updateTask(phaseIndex, taskIndex)
                        }
                        style={styles.checkbox}
                      />

                      <span
                        style={{
                          ...styles.taskText,
                          textDecoration: task.completed
                            ? "line-through"
                            : "none",
                          opacity: task.completed ? 0.55 : 1,
                        }}
                      >
                        {task.title}
                      </span>

                      {task.completed && (
                        <span style={styles.completedLabel}>
                          Done
                        </span>
                      )}
                    </label>
                  ))}
                </div>
              </section>
            );
          })}
        </div>

        <p style={styles.footer}>
          Small steps every day lead to big achievements.
          Keep moving forward! 💜
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
    maxWidth: "950px",
    margin: "0 auto",
  },
  backButton: {
    border: "none",
    background: "transparent",
    color: "#6558d3",
    fontSize: "14px",
    fontWeight: "600",
    cursor: "pointer",
    marginBottom: "25px",
  },
  hero: {
    background: "linear-gradient(135deg, #5144bd, #8175e8)",
    color: "white",
    padding: "38px",
    borderRadius: "20px",
    marginBottom: "25px",
    boxShadow: "0 12px 30px rgba(101,88,211,0.15)",
  },
  tag: {
    fontSize: "11px",
    letterSpacing: "2px",
    fontWeight: "700",
    opacity: 0.85,
  },
  heading: {
    fontSize: "32px",
    margin: "14px 0",
    overflowWrap: "anywhere",
  },
  description: {
    fontSize: "14px",
    lineHeight: 1.7,
    maxWidth: "650px",
    opacity: 0.9,
  },
  details: {
    display: "flex",
    flexWrap: "wrap",
    gap: "20px",
    marginTop: "25px",
    fontSize: "13px",
  },
  progressCard: {
    background: "white",
    padding: "25px",
    borderRadius: "18px",
    marginBottom: "30px",
    border: "1px solid #ececf4",
    boxShadow: "0 5px 18px rgba(50,40,100,0.04)",
  },
  progressHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
  },
  sectionTitle: {
    fontSize: "21px",
    color: "#25263a",
    margin: "0 0 8px",
  },
  muted: {
    color: "#85869a",
    fontSize: "13px",
    margin: 0,
    lineHeight: 1.6,
  },
  percentage: {
    fontSize: "27px",
    color: "#6558d3",
  },
  progressTrack: {
    height: "10px",
    background: "#eeeeF7",
    borderRadius: "20px",
    overflow: "hidden",
    marginTop: "22px",
  },
  progressFill: {
    height: "100%",
    background: "linear-gradient(90deg, #8e80ed, #5144bd)",
    borderRadius: "20px",
    transition: "width 0.3s ease",
  },
  progressText: {
    color: "#85869a",
    fontSize: "12px",
    marginBottom: 0,
    marginTop: "12px",
  },
  successMessage: {
    color: "#16834a",
    fontSize: "13px",
    fontWeight: "600",
    marginBottom: 0,
  },
  roadmapHeading: {
    marginBottom: "20px",
  },
  phases: {
    display: "grid",
    gap: "18px",
  },
  phaseCard: {
    background: "white",
    border: "1px solid #ececf4",
    borderRadius: "18px",
    padding: "25px",
    boxShadow: "0 5px 18px rgba(50,40,100,0.04)",
  },
  phaseHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    marginBottom: "20px",
  },
  phaseTag: {
    color: "#6558d3",
    fontSize: "11px",
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: "1px",
  },
  phaseTitle: {
    color: "#25263a",
    fontSize: "18px",
    margin: "7px 0 0",
  },
  duration: {
    background: "#f0efff",
    color: "#6558d3",
    padding: "7px 12px",
    borderRadius: "20px",
    fontSize: "12px",
    fontWeight: "600",
    whiteSpace: "nowrap",
  },
  phaseProgress: {
    marginBottom: "20px",
  },
  phaseProgressHeader: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: "12px",
    color: "#85869a",
    marginBottom: "8px",
  },
  smallProgressTrack: {
    height: "6px",
    background: "#eeeeF7",
    borderRadius: "20px",
    overflow: "hidden",
  },
  smallProgressFill: {
    height: "100%",
    background: "#8175e8",
    borderRadius: "20px",
    transition: "width 0.3s ease",
  },
  taskList: {
    display: "grid",
    gap: "15px",
  },
  task: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    color: "#55566b",
    fontSize: "14px",
    cursor: "pointer",
  },
  checkbox: {
    width: "17px",
    height: "17px",
    accentColor: "#6558d3",
    cursor: "pointer",
    flexShrink: 0,
  },
  taskText: {
    lineHeight: 1.5,
    flex: 1,
  },
  completedLabel: {
    color: "#16834a",
    fontSize: "11px",
    fontWeight: "700",
  },
  footer: {
    textAlign: "center",
    color: "#85869a",
    fontSize: "13px",
    marginTop: "30px",
  },
  errorCard: {
    maxWidth: "500px",
    margin: "80px auto",
    background: "white",
    padding: "30px",
    borderRadius: "16px",
    textAlign: "center",
  },
  primaryButton: {
    background: "#6558d3",
    color: "white",
    border: "none",
    borderRadius: "9px",
    padding: "12px 20px",
    cursor: "pointer",
  },
};

export default RoadmapPage;
