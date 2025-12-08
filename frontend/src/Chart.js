import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import { API_URL } from "./config";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function ProgressChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/get_progress/`)
      .then(res => res.json())
      .then(json => setData(json))
      .catch(err => console.error(err));
  }, []);

  const chartData = {
    labels: data.map(item => item.date),
    datasets: [
      {
        label: "Hmotnost (kg)",
        data: data.map(item => item.weight),
        fill: false,
        borderColor: "green",
        tension: 0.3,
      },
      {
        label: "Změna",
        data: data.map(item => item.change),
        fill: false,
        borderColor: "red",
        tension: 0.3,
      }
    ]
  };

  return (
    <div>
      <h2>Graf pokroku</h2>
      <Line data={chartData} options={{ responsive: true }} />
    </div>
  );
}
