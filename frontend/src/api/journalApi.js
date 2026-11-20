
import apiClient from "./apiClient";

const journalApi = {
  getEntries: () => apiClient.get("/journal"),

  getEntryById: (id) => apiClient.get(`/journal/${id}`),

  createEntry: (entryData) => apiClient.post("/journal", entryData),

  updateEntry: (id, entryData) =>
    apiClient.put(`/journal/${id}`, entryData),

  deleteEntry: (id) => apiClient.delete(`/journal/${id}`),
};

export default journalApi;
