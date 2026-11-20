
import { useCallback, useEffect, useState } from "react";

function useRoadmap(dreamId) {
  const [roadmap, setRoadmap] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    try {
      setLoading(true);

      const dreams = JSON.parse(
        localStorage.getItem("aspiraDreams") || "[]"
      );

      const selectedDream = dreams.find(
        (dream) => String(dream.id) === String(dreamId)
      );

      if (!selectedDream) {
        setRoadmap([]);
        setError("Dream not found.");
        return;
      }

      setRoadmap(selectedDream.roadmapTasks || []);
      setError("");
    } catch (err) {
      setError("Unable to load your roadmap.");
      setRoadmap([]);
    } finally {
      setLoading(false);
    }
  }, [dreamId]);

  const toggleTask = useCallback((phaseIndex, taskIndex) => {
    try {
      const dreams = JSON.parse(
        localStorage.getItem("aspiraDreams") || "[]"
      );

      const dreamIndex = dreams.findIndex(
        (dream) => String(dream.id) === String(dreamId)
      );

      if (dreamIndex === -1) {
        setError("Dream not found.");
        return;
      }

      const updatedRoadmap = (
        dreams[dreamIndex].roadmapTasks || []
      ).map((phase, index) => {
        if (index !== phaseIndex) return phase;

        return {
          ...phase,
          tasks: phase.tasks.map((task, index) => {
            if (index !== taskIndex) return task;

            if (typeof task === "string") {
              return {
                title: task,
                completed: true,
              };
            }

            return {
              ...task,
              completed: !task.completed,
            };
          }),
        };
      });

      dreams[dreamIndex].roadmapTasks = updatedRoadmap;

      localStorage.setItem(
        "aspiraDreams",
        JSON.stringify(dreams)
      );

      setRoadmap(updatedRoadmap);
      setError("");
    } catch (err) {
      setError("Unable to update task progress.");
    }
  }, [dreamId]);

  const totalTasks = roadmap.reduce((total, phase) => {
    return total + (phase.tasks?.length || 0);
  }, 0);

  const completedTasks = roadmap.reduce((total, phase) => {
    return (
      total +
      (phase.tasks || []).filter(
        (task) =>
          typeof task === "object" && task.completed
      ).length
    );
  }, 0);

  const progress =
    totalTasks > 0
      ? Math.round((completedTasks / totalTasks) * 100)
      : 0;

  return {
    roadmap,
    loading,
    error,
    toggleTask,
    totalTasks,
    completedTasks,
    progress,
  };
}

export default useRoadmap;
