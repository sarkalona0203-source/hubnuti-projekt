import React, { useState, useEffect, useMemo } from "react";
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

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);



const PristupPremium = () => {
  // --- Состояния ---
  const [paymentDone, setPaymentDone] = useState(false);
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [isLoggedIn, setIsLoggedIn] = useState(!!token);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [progressData, setProgressData] = useState([]);
  const [weight, setWeight] = useState("");
  const [note, setNote] = useState("");
  const [message, setMessage] = useState("");

  // --- Оплата ---
  const handlePayment = () => {
    // Здесь можно интегрировать Stripe/PayPal
    // Для примера просто отмечаем оплату как выполненную
    setPaymentDone(true);
    alert("✅ Оплата прошла успешно!");
  };

  // --- Регистрация ---
const handleRegister = async () => {
  if (!loginUsername || !loginPassword) {
    return setMessage("Vyplň uživatelské jméno a heslo!");
  }

  try {
    const res = await fetch(`${API_URL}/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: loginUsername, password: loginPassword }),
    });

    const data = await res.json();

    if (!res.ok) {
      // Показываем конкретную ошибку от сервера
      setMessage(data.error || JSON.stringify(data));
      return;
    }

    setMessage("✅ Registrace úspěšná! Můžeš se přihlásit.");
  } catch (err) {
    setMessage("Chyba sítě nebo serveru: " + err.message);
  }
};

// --- Вход ---
const handleLogin = async () => {
  if (!loginUsername || !loginPassword) {
    return setMessage("Vyplň uživatelské jméno a heslo!");
  }

  try {
    const res = await fetch(`${API_URL}/token/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: loginUsername, password: loginPassword }),
    });

    const data = await res.json();

    if (!res.ok) {
      // Показываем конкретную ошибку от сервера
      setMessage(data.error || data.non_field_errors?.[0] || JSON.stringify(data));
      return;
    }

    setToken(data.token);
    localStorage.setItem("token", data.token);
    setIsLoggedIn(true);
    setMessage("");
    await loadProgress(data.token);
  } catch (err) {
    setMessage("Chyba sítě nebo serveru: " + err.message);
  }
};
  // --- Выход ---
  const handleLogout = () => {
    setToken("");
    setIsLoggedIn(false);
    localStorage.removeItem("token");
    setProgressData([]);
  };

  // --- Загрузка прогресса ---
  const loadProgress = async (authToken) => {
    try {
      const res = await fetch(`${API_URL}/get_progress/`, {
        headers: { Authorization: `Token ${authToken}` },
      });
      if (!res.ok) throw new Error("Chyba při načítání dat.");
      const data = await res.json();
      setProgressData(data);
    } catch (err) {
      alert(err.message);
    }
  };

  // --- Добавление записи ---
  const addProgress = async () => {
    if (!weight) return alert("Vyplň váhu!");
    const weightFloat = parseFloat(weight.replace(",", "."));
    if (isNaN(weightFloat)) return alert("Neplatná hodnota!");
    try {
      const res = await fetch(`${API_URL}/add_progress/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Token ${token}` },
        body: JSON.stringify({ weight: weightFloat, note }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || "Chyba při přidávání váhy.");
      }
      setWeight("");
      setNote("");
      setMessage("Záznam byl uložen.");
      await loadProgress(token);
      setTimeout(() => setMessage(""), 5000);
    } catch (err) {
      alert(err.message);
    }
  };

  // --- Удаление записи ---
  const deleteProgress = async (id) => {
    if (!window.confirm("Opravdu smazat?")) return;
    try {
      const res = await fetch(`${API_URL}/delete_progress/${id}/`, {
        method: "DELETE",
        headers: { Authorization: `Token ${token}` },
      });
      if (!res.ok) throw new Error("Chyba při mazání záznamu.");
      await loadProgress(token);
    } catch (err) {
      alert(err.message);
    }
  };

  // --- Вычисление изменений веса ---
  const progressWithChange = useMemo(() => {
    let prevWeight = null;
    return progressData.map((item) => {
      const change = prevWeight !== null ? parseFloat((item.weight - prevWeight).toFixed(1)) : 0;
      let msg = "Začínáme! 💫";
      if (prevWeight !== null) {
        if (change < -0.3) msg = "Skvělý pokrok! 💪";
        else if (change > 0.3) msg = "Váha mírně vzrostla 🍽️";
        else msg = "Stabilní výsledek 🔄";
      }
      prevWeight = item.weight;
      return { ...item, change, message: msg };
    });
  }, [progressData]);

  // --- Данные для графика ---
  const chartData = {
    labels: progressData.map(d => new Date(d.date).toLocaleDateString()),
    datasets: [
      {
        label: "Váha (kg)",
        data: progressData.map(d => d.weight),
        borderColor: "rgba(255, 215, 0, 0.9)",
        backgroundColor: "rgba(255, 215, 0, 0.2)",
        pointBackgroundColor: progressData.map((d, i) => {
          if (i === 0) return "#FFD700";
          const diff = d.weight - progressData[i - 1].weight;
          return diff < -0.3 ? "#4CAF50" : diff > 0.3 ? "#FF4E50" : "#FFD700";
        }),
        pointRadius: 6,
        borderWidth: 3,
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: "top", labels: { color: "#fff" } },
      title: {
        display: true,
        text: "📈 Tvůj pokrok ve váze",
        color: "#fff",
        font: { size: 18, weight: "bold" },
      },
      tooltip: {
        callbacks: {
          label: ctx => {
            const note = progressData[ctx.dataIndex].note || "";
            return `${ctx.dataset.label}: ${ctx.raw} kg ${note ? `(${note})` : ""}`;
          },
        },
      },
    },
    scales: {
      x: { ticks: { color: "#eee" }, grid: { color: "rgba(255,255,255,0.1)" } },
      y: { ticks: { color: "#eee" }, grid: { color: "rgba(255,255,255,0.1)" } },
    },
  };

  // --- UI ---
  if (!paymentDone) {
    return (
      <div style={{ padding: "50px", textAlign: "center", color: "#fff" }}>
        <h1>💎 Premium Access</h1>
        <p>Než se zaregistruješ, je potřeba provést platbu.</p>
        <button onClick={handlePayment} style={{ padding: "12px 25px", background: "#FFD700", borderRadius: "8px", cursor: "pointer", fontWeight: "bold" }}>Zaplatit 💳</button>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div style={{ padding: "30px", textAlign: "center", color: "#fff" }}>
        <h1>🔒 Registrace / Přihlášení</h1>
        <input type="text" placeholder="Login" value={loginUsername} onChange={e => setLoginUsername(e.target.value)} style={{ padding: "10px", margin: "10px", borderRadius: "8px" }} />
        <input type="password" placeholder="Heslo" value={loginPassword} onChange={e => setLoginPassword(e.target.value)} style={{ padding: "10px", margin: "10px", borderRadius: "8px" }} />
        <br />
        <button onClick={handleRegister} style={{ padding: "10px 20px", background: "#4CAF50", margin: "5px", borderRadius: "8px", cursor: "pointer" }}>📝 Registrovat</button>
        <button onClick={handleLogin} style={{ padding: "10px 20px", background: "#FFD700", margin: "5px", borderRadius: "8px", cursor: "pointer" }}>🔓 Přihlásit</button>
      </div>
    );
  }

  // --- Основной UI для зарегистрированного пользователя ---
  return (
    <div style={{ padding: "30px", fontFamily: "Poppins, sans-serif", minHeight: "100vh", background: "linear-gradient(135deg, #0f2027, #203a43, #2c5364)", color: "white" }}>
      <div style={{ maxWidth: "900px", margin: "0 auto", background: "rgba(255,255,255,0.05)", borderRadius: "15px", padding: "25px" }}>
        <div style={{ textAlign: "right", marginBottom: "15px" }}>
          <button onClick={handleLogout} style={{ padding: "6px 12px", borderRadius: "6px", background: "#ff4e50", color: "#fff", cursor: "pointer" }}>🚪 Odhlásit</button>
        </div>

        {message && <div style={{ backgroundColor: "rgba(0,255,100,0.15)", color: "#80ff9f", padding: "10px", borderRadius: "6px", textAlign: "center", marginBottom: "20px" }}>{message}</div>}

        {/* Форма добавления веса */}
        <div style={{ display: "flex", gap: "10px", justifyContent: "center", marginBottom: "25px", flexWrap: "wrap" }}>
          <input type="number" step="0.1" placeholder="Váha (kg)" value={weight} onChange={e => setWeight(e.target.value)} style={{ padding: "10px", borderRadius: "8px", width: "160px" }} />
          <input type="text" placeholder="Poznámka" value={note} onChange={e => setNote(e.target.value)} style={{ padding: "10px", borderRadius: "8px", width: "250px" }} />
          <button onClick={addProgress} style={{ padding: "10px 18px", background: "linear-gradient(90deg, #FFD700, #FFA500)", borderRadius: "8px", fontWeight: "bold", cursor: "pointer" }}>➕ Uložit</button>
        </div>

        {/* График и таблица */}
        {progressWithChange.length > 0 && (
          <>
            <div style={{ marginBottom: "30px" }}>
              <Line data={chartData} options={chartOptions} />
            </div>

            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #555" }}>
                  <th>Datum</th>
                  <th>Váha (kg)</th>
                  <th>Změna</th>
                  <th>Progres</th>
                  <th>Poznámka</th>
                  <th>Akce</th>
                </tr>
              </thead>
              <tbody>
                {progressWithChange.map(item => {
                  const color = item.change < -0.3 ? "#4CAF50" : item.change > 0.3 ? "#FF5252" : "#FFC107";
                  return (
                    <tr key={item.id} style={{ backgroundColor: "rgba(255,255,255,0.05)" }}>
                      <td>{new Date(item.date).toLocaleDateString()}</td>
                      <td style={{ color }}>{item.weight}</td>
                      <td style={{ color }}>{item.change > 0 ? `+${item.change}` : item.change}</td>
                      <td>{item.message}</td>
                      <td>{item.note}</td>
                      <td><button onClick={() => deleteProgress(item.id)} style={{ padding: "5px 10px", borderRadius: "5px", background: "#ff4e50", color: "#fff", cursor: "pointer" }}>🗑️</button></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </>
        )}
      </div>
    </div>
  );
};

export default PristupPremium;