
import apiClient from "./apiClient";

const reminderApi = {
  // Get all reminders
  getReminders: () =>
    apiClient.get("/reminders"),

  // Create a new reminder
  createReminder: (data) =>
    apiClient.post("/reminders", data),

  // Update a reminder
  updateReminder: (reminderId, data) =>
    apiClient.put(`/reminders/${reminderId}`, data),

  // Delete a reminder
  deleteReminder: (reminderId) =>
    apiClient.delete(`/reminders/${reminderId}`),

  // Mark reminder as completed
  completeReminder: (reminderId) =>
    apiClient.patch(`/reminders/${reminderId}/complete`),
};

export default reminderApi;
