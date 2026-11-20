
/* ==============================
   ASPIRA FORMATTER FUNCTIONS
============================== */

// Format date into readable format
export function formatDate(date) {
  if (!date) return "Not available";

  const parsedDate = new Date(date);

  if (isNaN(parsedDate.getTime())) {
    return "Invalid date";
  }

  return parsedDate.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

// Format date and time
export function formatDateTime(date) {
  if (!date) return "Not available";

  const parsedDate = new Date(date);

  if (isNaN(parsedDate.getTime())) {
    return "Invalid date";
  }

  return parsedDate.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Capitalize first letter of a word
export function capitalize(text) {
  if (!text) return "";

  return text.charAt(0).toUpperCase() + text.slice(1);
}

// Convert text into title case
export function toTitleCase(text) {
  if (!text) return "";

  return text
    .toLowerCase()
    .split(" ")
    .map((word) => capitalize(word))
    .join(" ");
}

// Shorten long text
export function truncateText(text, maxLength = 100) {
  if (!text) return "";

  if (text.length <= maxLength) {
    return text;
  }

  return text.slice(0, maxLength).trim() + "...";
}

// Calculate progress percentage
export function formatProgress(completed, total) {
  if (!total || total <= 0) return 0;

  return Math.round((completed / total) * 100);
}

// Format duration in hours
export function formatHours(hours) {
  if (hours === undefined || hours === null) {
    return "Not specified";
  }

  return `${hours} ${Number(hours) === 1 ? "hour" : "hours"}`;
}

// Get user's initials
export function getInitials(name) {
  if (!name) return "U";

  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word.charAt(0).toUpperCase())
    .join("");
}

// Format task status
export function formatTaskStatus(completed) {
  return completed ? "Completed" : "Pending";
}

// Format a number with commas
export function formatNumber(number) {
  return Number(number || 0).toLocaleString("en-IN");
}
