
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

function TaskDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [dream, setDream] = useState(null);
  const [task, setTask] = useState(null);
  const [phase, setPhase] = useState(null);
  const [error, setError] = useState("");

  // Load the selected task from saved roadmaps
  useEffect(() => {
    try {
      const savedDreams = JSON.parse(
        localStorage.getItem("aspiraDreams") || "[]"
      );

      if (!Array.isArray(savedDreams)) {
        throw new Error("Invalid dream data");
      }

      let found = false;

      for (const savedDream of savedDreams) {
        const phases = Array.isArray(savedDream.roadmapTasks)
          ? savedDream.roadmapTasks
          : [];

        for (const savedPhase of phases) {
          const phaseTasks = Array.isArray(savedPhase.tasks)
            ? savedPhase.tasks
            : [];

          const selectedTask = phaseTasks.find((item) => {
            const taskTitle =
              typeof item === "string" ? item : item.title;

            return (
              String(item?.id || "") === String(id) ||
              String(taskTitle || "") === decodeURIComponent(id)
            );
          });

          if (selectedTask !== undefined) {
            const normalizedTask =
              typeof selectedTask === "string"
                ? {
                    title: selectedTask,
                    completed: false,
                  }
                : selectedTask;

            setDream(savedDream);
            setTask(normalizedTask);
            setPhase(savedPhase);
            found = true;
            break;
          }
        }

        if (found) break;
      }

      if (!found) {
        setError("Task not found. It may have been removed from your roadmap.");
      }
    } catch (err) {
      console.error("Task loading error:", err);
      setError("Unable to load task details.");
    }
  }, [id]);

  // Update task completion and save it
  const toggleCompletion = () => {
    try {
      const savedDreams = JSON.parse(
        localStorage.getItem("aspiraDreams") || "[]"
      );

      const updatedDream = {
        ...dream,
        roadmapTasks: dream.roadmapTasks.map((savedPhase) => {
          if (savedPhase.phase !== phase.phase) {
            return savedPhase;
          }

          return {
            ...savedPhase,
            tasks: savedPhase.tasks.map((savedTask) => {
              const title =
                typeof savedTask === "string"
                  ? savedTask
                  : savedTask.title;

              if (
                String(savedTask?.id || "") === String(id) ||
                String(title || "") === decodeURIComponent(id)
              ) {
                return {
                  ...(typeof savedTask === "string"
                    ? { title: savedTask }
                    : savedTask),
                  completed: !task.completed,
                };
              }

              return savedTask;
            }),
          };
        }),
      };

      const updatedDreams = savedDreams.map((item) =>
        String(item.id) === String(dream.id)
          ? updatedDream
          : item
      );

      localStorage.setItem(
        "aspiraDreams",
        JSON.stringify(updatedDreams)
      );

      setDream(updatedDream);
      setTask((prev) => ({
        ...prev,
        completed: !prev.completed,
      }));
    } catch (err) {
      console.error("Task update error:", err);
      setError("Unable to update task status. Please try again.");
    }
  };

  if (error) {
    return (
      <main style={styles.page}>
        <div style={styles.card}>
          <h2>Task unavailable</h2>
          <p style={styles.subtitle}>{error}</p>
          <button
            style={styles.button}
            onClick={() => navigate("/dreams")}
          >
            Back to Dashboard
          </button>
        </div>
      </main>
    );
  }

  if (!task || !dream) return null;

  return (
    <main style={styles.page}>
      <div style={styles.container}>

        <button
          style={styles.backButton}
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>

        <section style={styles.card}>

          <span style={styles.label}>
            ASPIRA • TASK DETAILS
          </span>

          <h1 style={styles.heading}>
            {task.title}
          </h1>

          <p style={styles.subtitle}>
            Review your learning activity and track your progress.
          </p>

          {/* Dream Information */}
          <div style={styles.infoBox}>
            <h3>My Dream</h3>
            <p>{dream.title}</p>
          </div>

          {/* Phase Information */}
          <div style={styles.infoBox}>
            <h3>Learning Phase</h3>
            <p>{phase.title}</p>
            <span style={styles.smallText}>
              {phase.phase} • {phase.duration}
            </span>
          </div>

          {/* Task Description */}
          <div style={styles.infoBox}>
            <h3>Task Description</h3>
            <p>
              Work on this learning activity, practice the required
              concepts and apply what you learn.
            </p>
          </div>

          {/* Task Status */}
          <div style={styles.infoBox}>
            <h3>Task Status</h3>

            <span
              style={
                task.completed
                  ? styles.completed
                  : styles.pending
              }
            >
              {task.completed
                ? "Completed ✓"
                : "Not Completed"}
            </span>
          </div>

          {/* Learning Resources */}
          <div style={styles.infoBox}>
            <h3>Learning Resources</h3>
            <p style={styles.smallText}>
              No learning resources have been added to this task yet.
            </p>
          </div>

          {/* Completion Button */}
          <button
            style={{
              ...styles.button,
              background: task.completed ? "#e8e6f8" : "#6558d3",
              color: task.completed ? "#6558d3" : "#fff",
            }}
            onClick={toggleCompletion}
          >
            {task.completed
              ? "Mark as Incomplete"
              : "Mark as Completed ✓"}
          </button>

        </section>

        <p style={styles.footer}>
          Every small achievement takes you closer to your dream. 💜
        </p>
      </div>
    </main>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #f5efff, #f4f6fc)",
    padding: "40px 20px",
  },
  container: {
    maxWidth: "800px",
    margin: "auto",
  },
  backButton: {
    border: "none",
    background: "transparent",
    color: "#6558d3",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer",
    marginBottom: "20px",
  },
  card: {
    background: "#fff",
    borderRadius: "20px",
    padding: "35px",
    boxShadow: "0 10px 30px rgba(89,54,145,0.10)",
  },
  label: {
    color: "#9169d5",
    fontSize: "12px",
    fontWeight: "bold",
    letterSpacing: "1px",
  },
  heading: {
    color: "#30284f",
    fontSize: "28px",
    marginTop: "18px",
    overflowWrap: "anywhere",
  },
  infoBox: {
    background: "#faf8ff",
    padding: "18px",
    borderRadius: "12px",
    marginTop: "18px",
    border: "1px solid #f0ecfa",
  },
  infoTitle: {
    color: "#30284f",
  },
  button: {
    marginTop: "25px",
    padding: "13px 22px",
    border: "none",
    borderRadius: "9px",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "14px",
  },
  subtitle: {
    color: "#81758f",
    lineHeight: 1.6,
  },
  completed: {
    color: "#258653",
    fontWeight: "bold",
  },
  pending: {
    color: "#b17a25",
    fontWeight: "bold",
  },
  smallText: {
    color: "#85869a",
    fontSize: "12px",
  },
  footer: {
    textAlign: "center",
    color: "#85869a",
    fontSize: "13px",
    marginTop: "25px",
  },
};

export default TaskDetailPage;
