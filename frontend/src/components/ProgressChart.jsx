
import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import "./ProgressChart.css";

const ProgressChart = ({ data = [] }) => {
  const chartData = data.length
    ? data
    : [
        { day: "Mon", progress: 0 },
        { day: "Tue", progress: 0 },
        { day: "Wed", progress: 0 },
        { day: "Thu", progress: 0 },
        { day: "Fri", progress: 0 },
        { day: "Sat", progress: 0 },
        { day: "Sun", progress: 0 },
      ];

  return (
    <div className="progress-chart-card">
      <div className="progress-chart-header">
        <div>
          <h3>Weekly Progress</h3>
          <p>Your learning activity this week</p>
        </div>

        <span className="chart-icon">📈</span>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData}>
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#eee5f5"
            />

            <XAxis
              dataKey="day"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#857493", fontSize: 12 }}
            />

            <YAxis
              domain={[0, 100]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#857493", fontSize: 12 }}
            />

            <Tooltip />

            <Bar
              dataKey="progress"
              fill="#9871c4"
              radius={[8, 8, 0, 0]}
              barSize={30}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ProgressChart;
