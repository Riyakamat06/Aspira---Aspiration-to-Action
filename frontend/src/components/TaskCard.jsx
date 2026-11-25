
import React from "react";
import "./TaskCard.css";

const TaskCard = ({ task, onStatusChange, onView }) => {
  if (!task) return null;

  const completed = task.status === "completed";

  return (
    <div className={`task-card ${completed ? "task-completed" : ""}`}>
      <div className="task-card-left">
        <div className="task-check">
          {completed ? "✓" : "○"}
        </div>

        <div className="task-details">
          <h3>{task.title || "Untitled Task"}</h3>

          <p>
            {task.description || "Continue working towards your learning goal."}
          </p>

          <div className="task-meta">
            <span>📚 {task.category || "Learning"}</span>
            {task.due_date && (
              <span>
                📅 {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="task-card-actions">
        <button
          className="task-view-btn"
          onClick={() => onView?.(task)}
        >
          View
        </button>

        <button
          className={`task-status-btn ${completed ? "completed-btn" : ""}`}
          onClick={() =>
            onStatusChange?.(
              task,
              completed ? "pending" : "completed"
            )
          }
        >
          {completed ? "Completed" : "Mark Done"}
        </button>
      </div>
    </div>
  );
};

export default TaskCard;
