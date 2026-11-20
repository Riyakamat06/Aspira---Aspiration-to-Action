
import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import "./Navbar.css";

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate("/login", { replace: true });
  };

  const closeMenu = () => setMenuOpen(false);

  const links = [
    { name: "Dashboard", path: "/dreams" },
    { name: "Create Dream", path: "/intake" },
    { name: "Journal", path: "/journal" },
    { name: "Analytics", path: "/analytics" },
    { name: "Chatbot", path: "/chat" },
    { name: "Validate Roadmap", path: "/roadmap-validation" },
    { name: "Profile", path: "/profile" },
    { name: "Settings", path: "/settings" },
  ];

  return (
    <nav className="aspira-navbar">
      <div className="navbar-container">
        <NavLink
          to="/dreams"
          className="navbar-logo"
          onClick={closeMenu}
        >
          <span className="logo-icon">✦</span>
          <span>ASPIRA</span>
        </NavLink>

        <button
          className="menu-toggle"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation"
          aria-expanded={menuOpen}
        >
          {menuOpen ? "✕" : "☰"}
        </button>

        <div className={`navbar-links ${menuOpen ? "active" : ""}`}>
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              onClick={closeMenu}
              className={({ isActive }) =>
                isActive ? "nav-link active-link" : "nav-link"
              }
            >
              {link.name}
            </NavLink>
          ))}

          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
