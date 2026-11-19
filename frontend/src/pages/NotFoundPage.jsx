
import { useNavigate } from "react-router-dom";

function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.icon}>🔍</div>

        <h1 style={styles.heading}>404</h1>

        <h2 style={styles.subheading}>Page Not Found</h2>

        <p style={styles.description}>
          Oops! The page you're looking for doesn't exist
          or may have been moved.
        </p>

        <button
          style={styles.button}
          onClick={() => navigate("/dreams")}
        >
          Back to Dashboard
        </button>

        <div style={styles.brand}>
          ASPIRA – Aspiration to Action
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #f5efff, #e9ddff)",
    fontFamily: "Arial, sans-serif",
    padding: "20px",
  },
  card: {
    background: "#ffffff",
    padding: "45px 35px",
    borderRadius: "22px",
    textAlign: "center",
    maxWidth: "450px",
    width: "100%",
    boxShadow: "0 10px 35px rgba(89,54,145,0.12)",
  },
  icon: {
    fontSize: "45px",
    marginBottom: "10px",
  },
  heading: {
    fontSize: "75px",
    color: "#8055d9",
    margin: "0",
  },
  subheading: {
    color: "#35234f",
    fontSize: "24px",
  },
  description: {
    color: "#81758f",
    lineHeight: "1.7",
    fontSize: "14px",
  },
  button: {
    background: "#8055d9",
    color: "#ffffff",
    border: "none",
    padding: "13px 25px",
    borderRadius: "9px",
    cursor: "pointer",
    fontSize: "15px",
    marginTop: "15px",
  },
  brand: {
    marginTop: "30px",
    color: "#9990a8",
    fontSize: "12px",
  },
};

export default NotFoundPage;
