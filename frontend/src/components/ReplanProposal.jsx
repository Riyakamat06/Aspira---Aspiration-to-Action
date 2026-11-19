
import React from "react";
import "./Components.css";

const ReplanProposal = ({ proposal, onAccept, onReject }) => {
  if (!proposal) {
    return null;
  }

  return (
    <div className="replan-proposal">
      <div className="proposal-header">
        <h3>🔄 Roadmap Update</h3>
        <span>New suggestion</span>
      </div>

      <p>
        Your progress can take a new direction. Here is a suggested
        adjustment to your roadmap.
      </p>

      <div className="proposal-content">
        <h4>{proposal.title || "Suggested Plan"}</h4>

        <p>
          {proposal.description ||
            "A revised plan has been suggested based on your progress."}
        </p>

        {proposal.steps && (
          <ul>
            {proposal.steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="proposal-actions">
        <button onClick={onAccept}>Accept New Plan</button>
        <button onClick={onReject}>Keep Current Plan</button>
      </div>
    </div>
  );
};

export default ReplanProposal;
