
import { Navigate, Outlet } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import Navbar from "./Navbar";

export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth();

  // Redirect users who are not logged in
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Display Navbar and the requested protected page
  return (
    <>
      <Navbar />
      <Outlet />
    </>
  );
}
