
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Progress.css';

const initialTasks = [
  { id: 1, title: 'Complete HTML and CSS fundamentals', category: 'Web Development', done: true },
  { id: 2, title: 'Practice JavaScript basics', category: 'Programming', done: true },
  { id: 3, title: 'Build a React mini project', category: 'Web Development', done: false },
  { id: 4, title: 'Learn database fundamentals', category: 'Database', done: false },
  { id: 5, title: 'Update career learning journal', category: 'Personal Growth', done: false },
];

const weeklyActivity = [
  { day: 'Mon', value: 65 },
  { day: 'Tue', value: 85 },
  { day: 'Wed', value: 45 },
  { day: 'Thu', value: 75 },
  { day: 'Fri', value: 35 },
  { day: 'Sat', value: 95 },
  { day: 'Sun', value: 55 },
];

function Progress() {
  const [tasks, setTasks] = useState(initialTasks);
  const [newTask, setNewTask] = useState('');

  const completed = tasks.filter((task) => task.done).length;
  const pending = tasks.length - completed;
  const percentage = tasks.length
    ? Math.round((completed / tasks.length) * 100)
    : 0;

  const toggleTask = (id) => {
    setTasks((current) =>
      current.map((task) =>
        task.id === id ? { ...task, done: !task.done } : task
      )
    );
  };

  const addTask = (e) => {
    e.preventDefault();
    if (!newTask.trim()) return;

    setTasks((current) => [
      ...current,
      {
        id: Date.now(),
        title: newTask.trim(),
        category: 'Personal Goal',
        done: false,
      },
    ]);
    setNewTask('');
  };

  return (
    <main className="progress-page">
      <Link to="/" className="progress-back">← Dashboard</Link>

      <header className="progress-header">
        <div>
          <span className="progress-eyebrow">YOUR DEVELOPMENT</span>
          <h1>Progress Tracker</h1>
          <p>Every completed task brings you closer to your dream.</p>
        </div>
        <div className="progress-date">WEEKLY OVERVIEW</div>
      </header>

      <section className="progress-stats">
        <article className="progress-stat">
          <span>Total tasks</span>
          <strong>{tasks.length}</strong>
          <small>All your learning activities</small>
        </article>
        <article className="progress-stat">
          <span>Completed</span>
          <strong>{completed}</strong>
          <small>Tasks successfully finished</small>
        </article>
        <article className="progress-stat">
          <span>Pending</span>
          <strong>{pending}</strong>
          <small>Tasks waiting for you</small>
        </article>
        <article className="progress-stat highlight-stat">
          <span>Completion rate</span>
          <strong>{percentage}%</strong>
          <small>Based on your task list</small>
        </article>
      </section>

      <section className="progress-content">
        <article className="progress-panel">
          <div className="panel-heading">
            <div>
              <h2>Weekly activity</h2>
              <p>Your learning activity throughout the week.</p>
            </div>
            <span className="panel-tag">This week</span>
          </div>

          <div className="activity-chart">
            {weeklyActivity.map((item) => (
              <div className="activity-column" key={item.day}>
                <div className="activity-bar-area">
                  <div
                    className="activity-bar"
                    style={{ height: `${item.value}%` }}
                    title={`${item.value}% sample activity`}
                  ></div>
                </div>
                <span>{item.day}</span>
              </div>
            ))}
          </div>
          <small className="chart-note">
            Illustrative weekly activity values. Connect real activity data later.
          </small>
        </article>

        <article className="progress-panel completion-panel">
          <h2>Overall completion</h2>
          <p>Your current task completion rate.</p>
          <div
            className="completion-circle"
            style={{ '--progress': `${percentage}%` }}
          >
            <div>
              <strong>{percentage}%</strong>
              <span>Completed</span>
            </div>
          </div>
          <p className="completion-message">
            {percentage === 100
              ? 'Amazing! You completed all your tasks.'
              : 'Keep going. Every small step matters!'}
          </p>
        </article>
      </section>

      <section className="progress-panel task-panel">
        <div className="panel-heading">
          <div>
            <h2>Learning activities</h2>
            <p>Manage your tasks and mark them as completed.</p>
          </div>
          <span className="task-count">{pending} remaining</span>
        </div>

        <form className="add-task-form" onSubmit={addTask}>
          <input
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="Enter a new learning task..."
          />
          <button type="submit">+ Add task</button>
        </form>

        <div className="task-list">
          {tasks.map((task) => (
            <label className={`task-item ${task.done ? 'task-complete' : ''}`} key={task.id}>
              <input
                type="checkbox"
                checked={task.done}
                onChange={() => toggleTask(task.id)}
              />
              <span className="custom-check"></span>
              <span className="task-title-group">
                <strong>{task.title}</strong>
                <small>{task.category}</small>
              </span>
              <span className={`task-status ${task.done ? 'done-status' : ''}`}>
                {task.done ? 'Completed' : 'Pending'}
              </span>
            </label>
          ))}
        </div>
      </section>
    </main>
  );
}

export default Progress;
