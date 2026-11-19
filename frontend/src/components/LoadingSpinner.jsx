
import React from "react";
import "./LoadingSpinner.css";

function LoadingSpinner({ message = "Please wait..." }) {
  return (
    <div className="loading-container" role="status" aria-live="polite">
      <div className="loading-spinner"></div>
      <h3>Loading</h3>
      <p>{message}</p>
    </div>
  );
}

export default LoadingSpinner;
