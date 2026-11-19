
import apiClient from "./apiClient";

const roadmapApi = {
  getRoadmap: (dreamId) =>
    apiClient.get(`/dreams/${dreamId}/roadmap`),

  generateRoadmap: (dreamId, preferences = {}) =>
    apiClient.post(`/dreams/${dreamId}/roadmap/generate`, preferences),

  updateRoadmap: (dreamId, roadmapData) =>
    apiClient.put(`/dreams/${dreamId}/roadmap`, roadmapData),

  regenerateRoadmap: (dreamId, preferences = {}) =>
    apiClient.post(`/dreams/${dreamId}/roadmap/regenerate`, preferences),
};

export default roadmapApi;
