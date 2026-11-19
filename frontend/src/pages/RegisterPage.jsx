
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    setError("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (form.name.trim().length < 2) {
      setError("Please enter your full name.");
      return;
    }

    if (form.password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      // Demo registration until backend is connected
      login({
        name: form.name.trim(),
        email: form.email.trim(),
      });

      navigate("/dreams");
    } catch {
      setError("Registration failed. Please try again.");
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-card">
        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <h2
            style={{
              color: "#6558d3",
              fontSize: "27px",
              letterSpacing: "3px",
              fontWeight: "800",
            }}
          >
            ASPIRA
          </h2>

          <p>Aspiration to Action</p>
        </div>

        <h1>Create account</h1>

        <p>
          Start your journey. Turn your aspirations into achievements.
        </p>

        {error && (
          <p
            role="alert"
            style={{
              color: "#d9364f",
              fontSize: "13px",
              marginTop: "12px",
            }}
          >
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit}>
          <label htmlFor="name">Full name</label>

          <input
            id="name"
            type="text"
            name="name"
            placeholder="Enter your full name"
            value={form.name}
            onChange={handleChange}
            autoComplete="name"
            required
          />

          <label htmlFor="email">Email address</label>

          <input
            id="email"
            type="email"
            name="email"
            placeholder="Enter your email"
            value={form.email}
            onChange={handleChange}
            autoComplete="email"
            required
          />

          <label htmlFor="password">Password</label>

          <div style={{ position: "relative" }}>
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Create a password"
              value={form.password}
              onChange={handleChange}
              autoComplete="new-password"
              style={{ paddingRight: "75px" }}
              required
            />

            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              style={{
                position: "absolute",
                right: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                width: "auto",
                margin: 0,
                padding: "5px",
                background: "transparent",
                color: "#6558d3",
                fontSize: "12px",
              }}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          <label htmlFor="confirmPassword">Confirm password</label>

          <input
            id="confirmPassword"
            type={showPassword ? "text" : "password"}
            name="confirmPassword"
            placeholder="Re-enter your password"
            value={form.confirmPassword}
            onChange={handleChange}
            autoComplete="new-password"
            required
          />

          <button type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Create Account →"}
          </button>
        </form>

        <p
          style={{
            textAlign: "center",
            marginTop: "25px",
            marginBottom: 0,
          }}
        >
          Already have an account?{" "}
          <Link to="/login">Sign in</Link>
        </p>

        <p
          style={{
            textAlign: "center",
            fontSize: "11px",
            marginTop: "22px",
            marginBottom: 0,
          }}
        >
          Every big achievement starts with a dream.
        </p>
      </div>
    </main>
  );
}

export default RegisterPage;
