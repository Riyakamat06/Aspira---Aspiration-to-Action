
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: "",
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

    if (form.password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      // Demo login until backend authentication is connected
      login({
        email: form.email.trim(),
        name: form.email.trim().split("@")[0],
      });

      navigate("/dreams");
    } catch {
      setError("Something went wrong. Please try again.");
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-card">
        <div style={{ textAlign: "center", marginBottom: "30px" }}>
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

        <h1>Welcome back!</h1>

        <p>Sign in to continue working towards your dreams.</p>

        {error && (
          <p style={{ color: "#dc2626", fontSize: "13px" }}>
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit}>
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
              placeholder="Enter your password"
              value={form.password}
              onChange={handleChange}
              autoComplete="current-password"
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

          <button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In →"}
          </button>
        </form>

        <p
          style={{
            textAlign: "center",
            marginTop: "25px",
            marginBottom: 0,
          }}
        >
          Don't have an account?{" "}
          <Link to="/register">Create account</Link>
        </p>

        <p
          style={{
            textAlign: "center",
            fontSize: "11px",
            marginTop: "22px",
            marginBottom: 0,
          }}
        >
          Your journey begins with one step.
        </p>
      </div>
    </main>
  );
}

export default LoginPage;
