import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
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
    fetch("/api/get_progress/")
      .then(res => res.json())
      .then(json => setData(json))
      .catch(err => console.error(err));
  }, []);

  const chartData = {
    labels: data.map(item => item.date), // даты
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

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      tooltip: {
        mode: "index",
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: false
      }
    }
  };

  return (
    <div>
      <h2>Graf pokroku</h2>
      <Line data={chartData} options={options} />
    </div>
  );
}