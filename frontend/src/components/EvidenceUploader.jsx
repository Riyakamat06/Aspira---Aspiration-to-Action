
import React, { useState } from "react";
import "./Components.css";

const EvidenceUploader = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [description, setDescription] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!file) {
      alert("Please select a file first.");
      return;
    }

    if (onUpload) {
      onUpload({ file, description });
    }

    setFile(null);
    setDescription("");
    e.target.reset();
  };

  return (
    <div className="evidence-uploader">
      <h3>📎 Upload Your Evidence</h3>
      <p>Show your progress by uploading certificates, screenshots or documents.</p>

      <form onSubmit={handleSubmit}>
        <label>Choose a file</label>
        <input
          type="file"
          accept="image/*,.pdf,.doc,.docx"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <label>Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what you have completed..."
          rows="3"
        />

        <button type="submit">Upload Evidence</button>
      </form>

      {file && <p>Selected: {file.name}</p>}
    </div>
  );
};

export default EvidenceUploader;
