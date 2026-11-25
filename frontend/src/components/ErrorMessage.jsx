
import React from "react";
import "./ErrorMessage.css";

function ErrorMessage({
  message = "Something went wrong. Please try again.",
  onRetry,
  onClose,
}) {
  return (
    <div className="error-message" role="alert">
      <div className="error-icon">⚠️</div>

      <div className="error-content">
        <h4>Oops! Something went wrong</h4>
        <p>{message}</p>

        {onRetry && (
          <button
            type="button"
            className="error-retry"
            onClick={onRetry}
          >
            Try Again
          </button>
        )}
      </div>

      {onClose && (
        <button
          type="button"
          className="error-close"
          onClick={onClose}
          aria-label="Close error message"
        >
          ×
        </button>
      )}
    </div>
  );
}

export default ErrorMessage;
