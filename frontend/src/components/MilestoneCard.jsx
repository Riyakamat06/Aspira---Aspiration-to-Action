
import React from "react";
import "./MilestoneCard.css";

const MilestoneCard = ({ milestone, onClick }) => {
  if (!milestone) return null;

  const completed =
    milestone.status === "completed" || milestone.completed === true;

  const progress = Math.min(
    100,
    Math.max(0, Number(milestone.progress) || 0)
  );

  const status = completed
    ? "Completed"
    : progress > 0
    ? "In Progress"
    : "Pending";

  const targetDate = milestone.target_date || milestone.targetDate;

  const formattedDate = targetDate
    ? new Date(targetDate).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : null;

  const handleKeyDown = (event) => {
    if (!onClick) return;

    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onClick();
    }
  };

  return (
    <div
      className={`milestone-card ${
        completed ? "completed" : progress > 0 ? "in-progress" : "pending"
      }`}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {/* Milestone Icon */}
      <div className="milestone-icon">
        {completed ? "✓" : progress > 0 ? "◷" : "✦"}
      </div>

      {/* Milestone Details */}
      <div className="milestone-content">
        <div className="milestone-heading">
          <h3>
            {milestone.title || "Untitled Milestone"}
          </h3>

          <span
            className={`milestone-status ${
              completed
                ? "done"
                : progress > 0
                ? "working"
                : "pending"
            }`}
          >
            {status}
          </span>
        </div>

        <p>
          {milestone.description ||
            "Keep learning and working towards this milestone."}
        </p>

        {/* Target Date */}
        {formattedDate && (
          <small className="milestone-date">
            📅 Target date: {formattedDate}
          </small>
        )}

        {/* Progress */}
        {typeof milestone.progress !== "undefined" && (
          <div className="milestone-progress-section">
            <div className="milestone-progress-info">
              <span>Progress</span>
              <strong>{completed ? 100 : progress}%</strong>
            </div>

            <div className="milestone-progress-bar">
              <div
                className="milestone-progress-fill"
                style={{
                  width: `${completed ? 100 : progress}%`,
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MilestoneCard;
