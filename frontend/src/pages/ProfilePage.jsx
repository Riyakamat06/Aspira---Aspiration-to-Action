
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

function ProfilePage() {
  const navigate = useNavigate();
  const { user, updateUser } = useAuth();

  const [profile, setProfile] = useState({
    name: user?.name || "",
    email: user?.email || "",
    career: user?.career || "",
    education: user?.education || "",
    skills: user?.skills || "",
    bio: user?.bio || "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;

    setProfile((previous) => ({
      ...previous,
      [name]: value,
    }));

    setMessage("");
    setError("");
  };

  // Save profile
  const handleSave = (e) => {
    e.preventDefault();

    if (profile.name.trim().length < 2) {
      setError("Please enter your full name.");
      return;
    }

    if (!profile.email.trim()) {
      setError("Please enter your email address.");
      return;
    }

    try {
      updateUser({
        ...profile,
        name: profile.name.trim(),
        email: profile.email.trim(),
        career: profile.career,
        education: profile.education.trim(),
        skills: profile.skills.trim(),
        bio: profile.bio.trim(),
      });

      setMessage("Your profile has been updated successfully! ✨");
      setError("");
    } catch {
      setError("Unable to update your profile. Please try again.");
      setMessage("");
    }
  };

  const initial = profile.name
    ? profile.name.trim().charAt(0).toUpperCase()
    : "U";

  return (
    <main style={styles.page}>
      <div style={styles.container}>

        {/* Back Button */}
        <button
          style={styles.back}
          onClick={() => navigate("/dreams")}
        >
          ← Back to Dashboard
        </button>

        {/* Heading */}
        <header style={styles.header}>
          <span style={styles.eyebrow}>
            YOUR ASPIRA ACCOUNT
          </span>

          <h1>Profile & Settings</h1>

          <p>
            Manage your personal information and career preferences.
          </p>
        </header>

        {/* Profile Card */}
        <section style={styles.card}>

          {/* Profile Header */}
          <div style={styles.profileHeader}>
            <div style={styles.avatar}>
              {initial}
            </div>

            <div>
              <h2>{profile.name || "Your Name"}</h2>
              <p style={styles.email}>
                {profile.email || "Your email address"}
              </p>

              <span style={styles.memberBadge}>
                ✨ ASPIRA Member
              </span>
            </div>
          </div>

          <div style={styles.divider} />

          {/* Profile Form */}
          <form onSubmit={handleSave}>

            <h3 style={styles.sectionTitle}>
              Personal Information
            </h3>

            <label style={styles.label} htmlFor="name">
              Full Name
            </label>

            <input
              id="name"
              style={styles.input}
              type="text"
              name="name"
              placeholder="Enter your full name"
              value={profile.name}
              onChange={handleChange}
              required
            />

            <label style={styles.label} htmlFor="email">
              Email Address
            </label>

            <input
              id="email"
              style={styles.input}
              type="email"
              name="email"
              placeholder="Enter your email"
              value={profile.email}
              onChange={handleChange}
              required
            />

            <div style={styles.divider} />

            <h3 style={styles.sectionTitle}>
              Education & Career
            </h3>

            <label style={styles.label} htmlFor="education">
              Education
            </label>

            <input
              id="education"
              style={styles.input}
              type="text"
              name="education"
              placeholder="Example: BCA, B.Tech, MBA"
              value={profile.education}
              onChange={handleChange}
            />

            <label style={styles.label} htmlFor="career">
              Career Interest
            </label>

            <select
              id="career"
              style={styles.input}
              name="career"
              value={profile.career}
              onChange={handleChange}
            >
              <option value="">Select your career interest</option>
              <option value="Web Development">Web Development</option>
              <option value="Data Science">Data Science</option>
              <option value="Artificial Intelligence">Artificial Intelligence</option>
              <option value="Software Development">Software Development</option>
              <option value="Engineering">Engineering</option>
              <option value="Medical">Medical</option>
              <option value="Business">Business</option>
              <option value="Arts and Design">Arts and Design</option>
              <option value="Other">Other</option>
            </select>

            <label style={styles.label} htmlFor="skills">
              Skills
            </label>

            <textarea
              id="skills"
              style={styles.textarea}
              name="skills"
              value={profile.skills}
              onChange={handleChange}
              placeholder="Example: HTML, CSS, JavaScript, C, Java..."
            />

            <div style={styles.divider} />

            <h3 style={styles.sectionTitle}>
              About Me
            </h3>

            <label style={styles.label} htmlFor="bio">
              Personal Introduction
            </label>

            <textarea
              id="bio"
              style={{
                ...styles.textarea,
                minHeight: "110px",
              }}
              name="bio"
              value={profile.bio}
              onChange={handleChange}
              placeholder="Write something about yourself, your interests and your goals..."
            />

            {/* Messages */}
            {error && (
              <p role="alert" style={styles.error}>
                {error}
              </p>
            )}

            {message && (
              <p role="status" style={styles.success}>
                {message}
              </p>
            )}

            {/* Save Button */}
            <button type="submit" style={styles.saveButton}>
              Save Changes ✨
            </button>

          </form>
        </section>

        {/* Extra Information */}
        <section style={styles.tipCard}>
          <span style={{ fontSize: "25px" }}>💡</span>

          <div>
            <h3>Build your career profile</h3>

            <p>
              Keep your education, skills and career interests updated.
              This information can help ASPIRA personalize your future
              career roadmap.
            </p>
          </div>
        </section>

      </div>
    </main>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #f7f6ff, #f4f6fc)",
    padding: "35px 20px",
  },
  container: {
    maxWidth: "850px",
    margin: "0 auto",
  },
  back: {
    border: "none",
    background: "transparent",
    color: "#6558d3",
    fontWeight: "600",
    cursor: "pointer",
    marginBottom: "25px",
  },
  header: {
    marginBottom: "30px",
  },
  eyebrow: {
    color: "#6558d3",
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "2px",
  },
  card: {
    background: "white",
    padding: "32px",
    borderRadius: "18px",
    border: "1px solid #ececf4",
    boxShadow: "0 8px 25px rgba(50,40,100,0.05)",
  },
  profileHeader: {
    display: "flex",
    alignItems: "center",
    gap: "20px",
    flexWrap: "wrap",
    marginBottom: "25px",
  },
  avatar: {
    width: "75px",
    height: "75px",
    borderRadius: "22px",
    background: "linear-gradient(135deg, #887ce9, #5144bd)",
    color: "white",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "30px",
    fontWeight: "bold",
    boxShadow: "0 5px 15px rgba(101,88,211,0.2)",
  },
  email: {
    color: "#85869a",
    fontSize: "13px",
    marginTop: "5px",
  },
  memberBadge: {
    display: "inline-block",
    background: "#f0efff",
    color: "#6558d3",
    padding: "6px 10px",
    borderRadius: "20px",
    fontSize: "11px",
    marginTop: "5px",
  },
  divider: {
    height: "1px",
    background: "#eeeeF5",
    margin: "25px 0",
  },
  sectionTitle: {
    color: "#393452",
    fontSize: "17px",
    marginBottom: "20px",
  },
  label: {
    display: "block",
    marginTop: "18px",
    marginBottom: "8px",
    fontWeight: "600",
    color: "#444258",
    fontSize: "13px",
  },
  input: {
    width: "100%",
    padding: "13px",
    border: "1px solid #dedee9",
    borderRadius: "10px",
    fontSize: "14px",
    boxSizing: "border-box",
    outlineColor: "#6558d3",
    background: "#fff",
  },
  textarea: {
    width: "100%",
    minHeight: "85px",
    padding: "13px",
    border: "1px solid #dedee9",
    borderRadius: "10px",
    fontSize: "14px",
    boxSizing: "border-box",
    resize: "vertical",
    fontFamily: "inherit",
    outlineColor: "#6558d3",
  },
  saveButton: {
    marginTop: "25px",
    padding: "13px 25px",
    background: "linear-gradient(135deg, #7567df, #5144bd)",
    color: "white",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontWeight: "600",
    boxShadow: "0 5px 12px rgba(101,88,211,0.18)",
  },
  success: {
    color: "#21875e",
    background: "#eaf8f1",
    padding: "12px",
    borderRadius: "8px",
    fontSize: "13px",
    marginTop: "18px",
  },
  error: {
    color: "#c62840",
    background: "#fff0f1",
    padding: "12px",
    borderRadius: "8px",
    fontSize: "13px",
    marginTop: "18px",
  },
  tipCard: {
    display: "flex",
    gap: "15px",
    alignItems: "flex-start",
    background: "#eeedff",
    color: "#454078",
    padding: "22px",
    borderRadius: "15px",
    marginTop: "22px",
  },
};

export default ProfilePage;
