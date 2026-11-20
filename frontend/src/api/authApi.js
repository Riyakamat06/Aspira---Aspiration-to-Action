
import apiClient from "./apiClient";

const authApi = {
  register: (userData) => apiClient.post("/auth/register", userData),

  login: (credentials) => apiClient.post("/auth/login", credentials),

  getProfile: () => apiClient.get("/auth/me"),

  logout: () => apiClient.post("/auth/logout", {}),
};

export default authApi;
