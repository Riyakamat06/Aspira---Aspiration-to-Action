
import apiClient from "./apiClient";

const dreamApi = {
  getAllDreams: () => apiClient.get("/dreams"),

  getDreamById: (id) => apiClient.get(`/dreams/${id}`),

  createDream: (dreamData) => apiClient.post("/dreams", dreamData),

  updateDream: (id, dreamData) =>
    apiClient.put(`/dreams/${id}`, dreamData),

  deleteDream: (id) => apiClient.delete(`/dreams/${id}`),
};

export default dreamApi;
