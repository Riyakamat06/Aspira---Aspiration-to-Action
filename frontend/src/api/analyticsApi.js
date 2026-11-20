
import apiClient from "./apiClient";

const analyticsApi = {
  // Get overall progress
  getOverallProgress: () =>
    apiClient.get("/analytics/progress"),

  // Get weekly progress
  getWeeklyProgress: () =>
    apiClient.get("/analytics/weekly-progress"),

  // Get roadmap progress
  getRoadmapProgress: (roadmapId) =>
    apiClient.get(`/analytics/roadmap/${roadmapId}`),

  // Get completed and pending task statistics
  getTaskStatistics: () =>
    apiClient.get("/analytics/task-statistics"),

  // Get dashboard summary
  getDashboardSummary: () =>
    apiClient.get("/analytics/dashboard"),
};

export default analyticsApi;
