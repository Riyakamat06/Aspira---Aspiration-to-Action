
import React from "react";
import "./StatusToggle.css";

const StatusToggle = ({ status = "pending", onChange, disabled = false }) => {
  const statuses = [
    { value: "pending", label: "Pending" },
    { value: "in_progress", label: "In Progress" },
    { value: "completed", label: "Completed" },
  ];

  return (
    <div className="status-toggle">
      {statuses.map((item) => (
        <button
          key={item.value}
          type="button"
          disabled={disabled}
          onClick={() => onChange?.(item.value)}
          className={`status-option ${
            status === item.value ? `selected ${item.value}` : ""
          }`}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
};

export default StatusToggle;
