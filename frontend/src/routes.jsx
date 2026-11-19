
import { Navigate, Route, Routes } from "react-router-dom";

// Authentication pages
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

// Main pages
import DreamListPage from "./pages/DreamListPage";
import IntakePage from "./pages/IntakePage";
import RoadmapPage from "./pages/RoadmapPage";
import TaskDetailPage from "./pages/TaskDetailPage";

// Learning and progress
import JournalPage from "./pages/JournalPage";
import AnalyticsPage from "./pages/AnalyticsPage";

// AI Assistant
import ChatPage from "./pages/ChatPage";

// User pages
import ProfilePage from "./pages/ProfilePage";
import SettingsPage from "./pages/SettingsPage";

// Additional pages
import RoadmapValidationPage from "./pages/RoadmapValidationPage";
import NotFoundPage from "./pages/NotFoundPage";

// Components
import ProtectedRoute from "./components/ProtectedRoute";

function AppRoutes() {
  return (
    <Routes>
      {/* Default Route */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/dreams" element={<DreamListPage />} />
        <Route path="/dashboard" element={<Navigate to="/dreams" replace />} />
        <Route path="/intake" element={<IntakePage />} />

        {/* Roadmaps */}
        <Route path="/roadmap/:id" element={<RoadmapPage />} />
        <Route path="/roadmap-validation" element={<RoadmapValidationPage />} />

        {/* Tasks */}
        <Route path="/tasks/:id" element={<TaskDetailPage />} />

        {/* Learning and Progress */}
        <Route path="/journal" element={<JournalPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />

        {/* AI Assistant */}
        <Route path="/chat" element={<ChatPage />} />

        {/* User Profile */}
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      {/* 404 Page */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default AppRoutes;
