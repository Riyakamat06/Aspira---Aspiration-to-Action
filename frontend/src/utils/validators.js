
/* ==============================
   ASPIRA FORM VALIDATIONS
============================== */

// Validate email address
export function validateEmail(email) {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!email || !email.trim()) {
    return "Email address is required.";
  }

  if (!emailPattern.test(email.trim())) {
    return "Please enter a valid email address.";
  }

  return "";
}

// Validate password
export function validatePassword(password) {
  if (!password) {
    return "Password is required.";
  }

  if (password.length < 6) {
    return "Password must contain at least 6 characters.";
  }

  return "";
}

// Validate password confirmation
export function validateConfirmPassword(password, confirmPassword) {
  if (!confirmPassword) {
    return "Please confirm your password.";
  }

  if (password !== confirmPassword) {
    return "Passwords do not match.";
  }

  return "";
}

// Validate user's name
export function validateName(name) {
  if (!name || !name.trim()) {
    return "Name is required.";
  }

  if (name.trim().length < 2) {
    return "Name must contain at least 2 characters.";
  }

  return "";
}

// Validate dream title
export function validateDreamTitle(title) {
  if (!title || !title.trim()) {
    return "Please enter your dream or career goal.";
  }

  if (title.trim().length < 3) {
    return "Dream title must contain at least 3 characters.";
  }

  return "";
}

// Validate dream description
export function validateDescription(description) {
  if (!description || !description.trim()) {
    return "Please provide a description.";
  }

  if (description.trim().length < 10) {
    return "Description must contain at least 10 characters.";
  }

  return "";
}

// Validate daily journal entry
export function validateJournalEntry(entry) {
  if (!entry || !entry.trim()) {
    return "Journal content cannot be empty.";
  }

  if (entry.trim().length < 5) {
    return "Please write a little more about your learning.";
  }

  return "";
}

// Validate complete registration form
export function validateRegistration(form) {
  const errors = {};

  const nameError = validateName(form.name);
  const emailError = validateEmail(form.email);
  const passwordError = validatePassword(form.password);
  const confirmError = validateConfirmPassword(
    form.password,
    form.confirmPassword
  );

  if (nameError) errors.name = nameError;
  if (emailError) errors.email = emailError;
  if (passwordError) errors.password = passwordError;
  if (confirmError) errors.confirmPassword = confirmError;

  return errors;
}

// Check whether a form has any errors
export function hasErrors(errors) {
  return Object.keys(errors).length > 0;
}
