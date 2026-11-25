
import apiClient from "./apiClient";

const taskApi = {
  getTasks: (dreamId) =>
    apiClient.get(`/dreams/${dreamId}/tasks`),

  getTaskById: (taskId) =>
    apiClient.get(`/tasks/${taskId}`),

  updateTask: (taskId, taskData) =>
    apiClient.put(`/tasks/${taskId}`, taskData),

  updateTaskStatus: (taskId, completed) =>
    apiClient.patch(`/tasks/${taskId}/status`, { completed }),

  deleteTask: (taskId) =>
    apiClient.delete(`/tasks/${taskId}`),
};

export default taskApi;
