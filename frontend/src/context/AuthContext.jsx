
import React, { createContext, useState } from "react";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("aspira_user")) || null;
    } catch {
      return null;
    }
  });

  const login = (userData, token) => {
    localStorage.setItem("aspira_user", JSON.stringify(userData));

    if (token) {
      localStorage.setItem("aspira_token", token);
    }

    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("aspira_user");
    localStorage.removeItem("aspira_token");
    setUser(null);
  };

  const updateUser = (updatedData) => {
    const updatedUser = { ...user, ...updatedData };
    localStorage.setItem("aspira_user", JSON.stringify(updatedUser));
    setUser(updatedUser);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        updateUser,
        isAuthenticated: Boolean(user),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthContext;
