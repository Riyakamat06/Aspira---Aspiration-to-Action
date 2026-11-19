
import apiClient from "./apiClient";

const evidenceApi = {
  // Upload evidence for a task
  uploadEvidence: (taskId, formData) =>
    apiClient.post(`/evidence/${taskId}`, formData),

  // Get evidence for a particular task
  getTaskEvidence: (taskId) =>
    apiClient.get(`/evidence/${taskId}`),

  // Get all uploaded evidence
  getAllEvidence: () =>
    apiClient.get("/evidence"),

  // Delete uploaded evidence
  deleteEvidence: (evidenceId) =>
    apiClient.delete(`/evidence/${evidenceId}`),
};

export default evidenceApi;
