
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";

function SettingsPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // Load saved preferences
  const [settings, setSettings] = useState(() => {
    try {
      const saved = JSON.parse(
        localStorage.getItem("aspiraSettings") || "{}"
      );

      return {
        notifications: saved.notifications ?? true,
        weeklyReport: saved.weeklyReport ?? true,
        darkMode: saved.darkMode ?? false,
      };
    } catch {
      return {
        notifications: true,
        weeklyReport: true,
        darkMode: false,
      };
    }
  });

  const [message, setMessage] = useState("");

  // Save preferences whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(
        "aspiraSettings",
        JSON.stringify(settings)
      );
    } catch (error) {
      console.error("Unable to save settings:", error);
    }
  }, [settings]);

  // Update a setting
  const updateSetting = (name, value) => {
    setSettings((previous) => ({
      ...previous,
      [name]: value,
    }));

    setMessage("Settings updated successfully!");
  };

  // Clear chatbot history
  const clearChatHistory = () => {
    const confirmed = window.confirm(
      "Are you sure you want to clear your chatbot conversation history?"
    );

    if (!confirmed) return;

    localStorage.removeItem("aspiraChatHistory");
    setMessage("Chat history cleared successfully! ✨");
  };

  // Sign out
  const handleLogout = () => {
    const confirmed = window.confirm(
      "Are you sure you want to sign out of ASPIRA?"
    );

    if (!confirmed) return;

    logout();
    navigate("/login");
  };

  const dark = settings.darkMode;

  const theme = dark
    ? {
        page: "#171629",
        card: "#24223b",
        text: "#f5f2ff",
        muted: "#b9b3d0",
        border: "#393550",
        accent: "#a99aff",
        note: "#34304f",
      }
    : {
        page: "#f6f5fc",
        card: "#ffffff",
        text: "#302b49",
        muted: "#817b95",
        border: "#eeeaf5",
        accent: "#6558d3",
        note: "#f0efff",
      };

  return (
    <main
      style={{
        ...styles.page,
        background: theme.page,
        color: theme.text,
      }}
    >
      <div style={styles.container}>

        {/* Heading */}
        <header style={styles.header}>
          <span style={styles.label}>
            ASPIRA SETTINGS
          </span>

          <h1>Settings ⚙️</h1>

          <p style={{ color: theme.muted }}>
            Personalize your ASPIRA experience.
          </p>
        </header>

        {/* Success Message */}
        {message && (
          <div
            role="status"
            style={{
              ...styles.message,
              background: dark ? "#244b3c" : "#eaf8f1",
              color: dark ? "#b6f0d4" : "#21875e",
            }}
          >
            {message}
          </div>
        )}

        {/* Notification Settings */}
        <section
          style={{
            ...styles.card,
            background: theme.card,
            borderColor: theme.border,
          }}
        >
          <h2 style={{ color: theme.text }}>
            🔔 Notifications
          </h2>

          <SettingItem
            title="Task Notifications"
            description="Enable reminders about your pending roadmap tasks."
            checked={settings.notifications}
            onChange={(value) =>
              updateSetting("notifications", value)
            }
            theme={theme}
          />

          <SettingItem
            title="Weekly Progress Report"
            description="Enable your weekly learning progress report preference."
            checked={settings.weeklyReport}
            onChange={(value) =>
              updateSetting("weeklyReport", value)
            }
            theme={theme}
          />
        </section>

        {/* Appearance Settings */}
        <section
          style={{
            ...styles.card,
            background: theme.card,
            borderColor: theme.border,
          }}
        >
          <h2 style={{ color: theme.text }}>
            🎨 Appearance
          </h2>

          <SettingItem
            title="Dark Mode"
            description="Change the appearance of this Settings page."
            checked={settings.darkMode}
            onChange={(value) =>
              updateSetting("darkMode", value)
            }
            theme={theme}
          />

          <p
            style={{
              ...styles.note,
              color: theme.muted,
              background: theme.note,
            }}
          >
            Your appearance preference is saved. Dark mode currently
            applies only to this page.
          </p>
        </section>

        {/* Account Information */}
        <section
          style={{
            ...styles.card,
            background: theme.card,
            borderColor: theme.border,
          }}
        >
          <h2 style={{ color: theme.text }}>
            👤 Account Information
          </h2>

          <div style={styles.accountItem}>
            <span style={{ color: theme.muted }}>
              Full Name
            </span>

            <strong>{user?.name || "Not available"}</strong>
          </div>

          <div style={styles.accountItem}>
            <span style={{ color: theme.muted }}>
              Email Address
            </span>

            <strong>{user?.email || "Not available"}</strong>
          </div>

          <button
            style={styles.secondaryButton}
            onClick={() => navigate("/profile")}
          >
            Edit Profile →
          </button>
        </section>

        {/* Privacy and Chat */}
        <section
          style={{
            ...styles.card,
            background: theme.card,
            borderColor: theme.border,
          }}
        >
          <h2 style={{ color: theme.text }}>
            🔐 Privacy & Chat
          </h2>

          <p
            style={{
              ...styles.description,
              color: theme.muted,
            }}
          >
            Your career goals and learning progress are part of your
            personal ASPIRA journey. Keep your account credentials private.
          </p>

          <div style={styles.actionRow}>
            <div>
              <h3 style={{ color: theme.text }}>
                Clear Chat History
              </h3>

              <p style={{ color: theme.muted }}>
                Delete your saved chatbot conversations.
              </p>
            </div>

            <button
              style={styles.dangerButton}
              onClick={clearChatHistory}
            >
              Clear Chat
            </button>
          </div>
        </section>

        {/* Sign Out */}
        <section
          style={{
            ...styles.card,
            background: theme.card,
            borderColor: theme.border,
          }}
        >
          <h2 style={{ color: theme.text }}>
            🚪 Sign Out
          </h2>

          <p
            style={{
              ...styles.description,
              color: theme.muted,
            }}
          >
            Sign out of your ASPIRA account on this browser.
          </p>

          <button
            style={styles.logoutButton}
            onClick={handleLogout}
          >
            Sign Out →
          </button>
        </section>

      </div>
    </main>
  );
}

// Reusable settings switch
function SettingItem({
  title,
  description,
  checked,
  onChange,
  theme,
}) {
  return (
    <div
      style={{
        ...styles.settingItem,
        borderBottomColor: theme.border,
      }}
    >
      <div>
        <h3 style={{ color: theme.text }}>
          {title}
        </h3>

        <p style={{ color: theme.muted }}>
          {description}
        </p>
      </div>

      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        style={styles.checkbox}
        aria-label={title}
      />
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    padding: "40px 20px",
    transition: "background 0.3s ease, color 0.3s ease",
  },
  container: {
    maxWidth: "850px",
    margin: "auto",
  },
  header: {
    marginBottom: "28px",
  },
  label: {
    color: "#9169d5",
    fontSize: "12px",
    fontWeight: "bold",
    letterSpacing: "1.5px",
  },
  card: {
    padding: "25px",
    borderRadius: "18px",
    marginBottom: "20px",
    border: "1px solid",
    boxShadow: "0 8px 25px rgba(89,54,145,0.06)",
  },
  settingItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "15px",
    padding: "17px 0",
    borderBottom: "1px solid",
  },
  checkbox: {
    width: "20px",
    height: "20px",
    accentColor: "#8055d9",
    cursor: "pointer",
    flexShrink: 0,
  },
  description: {
    fontSize: "14px",
    lineHeight: "1.7",
  },
  note: {
    padding: "13px",
    borderRadius: "9px",
    fontSize: "12px",
    marginTop: "15px",
    lineHeight: 1.6,
  },
  message: {
    padding: "13px 16px",
    borderRadius: "10px",
    marginBottom: "20px",
    fontSize: "13px",
  },
  accountItem: {
    display: "flex",
    justifyContent: "space-between",
    flexWrap: "wrap",
    gap: "10px",
    padding: "14px 0",
    borderBottom: "1px solid #eeeaf5",
    fontSize: "13px",
  },
  actionRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "15px",
    marginTop: "20px",
  },
  secondaryButton: {
    marginTop: "18px",
    padding: "11px 18px",
    background: "#6558d3",
    color: "white",
    border: "none",
    borderRadius: "9px",
    cursor: "pointer",
    fontWeight: "600",
  },
  dangerButton: {
    padding: "10px 16px",
    background: "#fff0f1",
    color: "#d9364f",
    border: "none",
    borderRadius: "9px",
    cursor: "pointer",
    fontWeight: "600",
  },
  logoutButton: {
    padding: "12px 22px",
    background: "#d9364f",
    color: "white",
    border: "none",
    borderRadius: "9px",
    cursor: "pointer",
    fontWeight: "600",
    marginTop: "12px",
  },
};

export default SettingsPage;
