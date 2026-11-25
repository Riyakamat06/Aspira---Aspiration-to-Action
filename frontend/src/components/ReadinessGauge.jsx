
import React from "react";
import "./ReadinessGauge.css";

const ReadinessGauge = ({ score = 0, title = "Career Readiness" }) => {
  const safeScore = Math.min(100, Math.max(0, Number(score) || 0));

  const getStatus = () => {
    if (safeScore >= 80) return "Excellent";
    if (safeScore >= 60) return "Good";
    if (safeScore >= 40) return "Developing";
    return "Getting Started";
  };

  return (
    <div className="readiness-card">
      <div className="readiness-header">
        <div>
          <h3>{title}</h3>
          <p>Your journey towards career readiness</p>
        </div>
        <span className="readiness-icon">🎯</span>
      </div>

      <div className="gauge-container">
        <div
          className="gauge-circle"
          style={{
            background: `conic-gradient(#986ac7 ${safeScore * 3.6}deg, #eee5f5 0deg)`,
          }}
        >
          <div className="gauge-inner">
            <h2>{safeScore}%</h2>
            <span>Ready</span>
          </div>
        </div>
      </div>

      <div className="readiness-result">
        <span className="readiness-status">{getStatus()}</span>
        <p>Keep learning and completing your roadmap tasks!</p>
      </div>
    </div>
  );
};

export default ReadinessGauge;
