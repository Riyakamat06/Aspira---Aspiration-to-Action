
import React, { useState } from "react";
import "./Components.css";

const ReminderSettings = ({ onSave }) => {
  const [enabled, setEnabled] = useState(true);
  const [frequency, setFrequency] = useState("daily");
  const [reminderTime, setReminderTime] = useState("18:00");

  const handleSave = () => {
    const settings = {
      enabled,
      frequency,
      reminderTime,
    };

    if (onSave) {
      onSave(settings);
    }

    alert("Reminder settings saved!");
  };

  return (
    <div className="reminder-settings">
      <h3>⏰ Study Reminders</h3>
      <p>Stay consistent and keep moving towards your dream.</p>

      <label>
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => setEnabled(e.target.checked)}
        />
        Enable reminders
      </label>

      <div>
        <label>Reminder frequency</label>
        <select
          value={frequency}
          onChange={(e) => setFrequency(e.target.value)}
          disabled={!enabled}
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
        </select>
      </div>

      <div>
        <label>Reminder time</label>
        <input
          type="time"
          value={reminderTime}
          onChange={(e) => setReminderTime(e.target.value)}
          disabled={!enabled}
        />
      </div>

      <button type="button" onClick={handleSave}>
        Save Reminder
      </button>
    </div>
  );
};

export default ReminderSettings;
