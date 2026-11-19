
import React from "react";
import "./DisclaimerBanner.css";

function DisclaimerBanner({ message, type = "info", onClose }) {
  return (
    <div className={`disclaimer-banner disclaimer-${type}`}>
      <div className="disclaimer-icon">
        {type === "warning" ? "⚠️" : "💡"}
      </div>

      <div className="disclaimer-content">
        <h4>{type === "warning" ? "Important Notice" : "A Friendly Reminder"}</h4>
        <p>
          {message ||
            "ASPIRA provides AI-generated career guidance for informational purposes only. Explore the suggestions and make decisions based on your own interests, research, and circumstances."}
        </p>
      </div>

      {onClose && (
        <button
          type="button"
          className="disclaimer-close"
          onClick={onClose}
          aria-label="Close notice"
        >
          ×
        </button>
      )}
    </div>
  );
}

export default DisclaimerBanner;
