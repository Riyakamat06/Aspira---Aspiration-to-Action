
import React from "react";
import { useNavigate } from "react-router-dom";
import "./DreamCard.css";

const DreamCard = ({ dream, onEdit, onDelete }) => {
  const navigate = useNavigate();

  if (!dream) return null;

  // Calculate task progress from the saved roadmap
  const tasks = Array.isArray(dream.roadmapTasks)
    ? dream.roadmapTasks.flatMap((phase) =>
        Array.isArray(phase.tasks) ? phase.tasks : []
      )
    : [];

  const completedTasks = tasks.filter(
    (task) =>
      typeof task === "object" && task !== null && task.completed
  ).length;

  const totalTasks = tasks.length;

  const progress =
    totalTasks > 0
      ? Math.round((completedTasks / totalTasks) * 100)
      : Math.min(100, Math.max(0, Number(dream.progress) || 0));

  const pendingTasks = totalTasks - completedTasks;

  const handleViewRoadmap = () => {
    navigate(`/roadmap/${dream.id}`);
  };

  return (
    <div className="dream-card">

      {/* Card Header */}
      <div className="dream-card-header">
        <span className="dream-icon">✦</span>

        <span className="dream-category">
          {dream.category || "Career Goal"}
        </span>
      </div>

      {/* Dream Details */}
      <h3>
        {dream.title || dream.name || "Untitled Dream"}
      </h3>

      <p className="dream-description">
        {dream.description ||
          "Your journey towards achieving this dream starts here."}
      </p>

      {/* Learning Information */}
      <div className="dream-meta">
        <div>
          <span>Current Level</span>
          <strong>{dream.currentLevel || "Beginner"}</strong>
        </div>

        <div>
          <span>Target Timeline</span>
          <strong>{dream.timeline || "Not specified"}</strong>
        </div>
      </div>

      {/* Progress Section */}
      <div className="dream-progress-section">
        <div className="dream-progress-info">
          <span>Overall Progress</span>
          <strong>{progress}%</strong>
        </div>

        <div
          className="dream-progress-bar"
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Dream completion progress"
        >
          <div
            className="dream-progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Task Summary */}
      {totalTasks > 0 && (
        <div className="dream-task-summary">
          <span>✅ {completedTasks} Completed</span>
          <span>⏳ {pendingTasks} Pending</span>
        </div>
      )}

      {/* Actions */}
      <div className="dream-card-actions">
        <button
          type="button"
          className="dream-view-btn"
          onClick={handleViewRoadmap}
        >
          View Roadmap →
        </button>

        {onEdit && (
          <button
            type="button"
            className="dream-edit-btn"
            onClick={() => onEdit(dream)}
          >
            Edit
          </button>
        )}

        {onDelete && (
          <button
            type="button"
            className="dream-delete-btn"
            onClick={() => onDelete(dream)}
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
};

export default DreamCard;
