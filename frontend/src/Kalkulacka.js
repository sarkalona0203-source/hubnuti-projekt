import React, { useState } from "react";
import "./kalkulacka.css";
import { API_URL, getImageUrl, MEDIA_URL } from "./config";

const INITIAL_FORM = {
  vaha: "",
  vyska: "",
  vek: "",
  pohlavi: "muz",
  aktivita: "sedavy",
};

const dny = ["pondeli", "utery", "streda", "ctvrtek", "patek", "sobota", "nedele"];

const typyMap = {
  snidane: "Snídaně",
  druhe_snidane: "Druhá snídaně",
  obed: "Oběd",
  svacina: "Svačina",
  vecere: "Večeře",
  extra_snack: "Extra snack",
};

// ✅ Лимит именно на обновления
const MAX_REFRESH_COUNT = 5;

export default function Kalkulacka() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [manualCalories, setManualCalories] = useState("");
  const [vysledek, setVysledek] = useState(null);
  const [lastForm, setLastForm] = useState(null);
  const [refreshCount, setRefreshCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [openIngredients, setOpenIngredients] = useState({});

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const toggleIngredients = (den, index) => {
    setOpenIngredients((prev) => ({
      ...prev,
      [`${den}-${index}`]: !prev[`${den}-${index}`],
    }));
  };

  const fetchData = async (url, body = null) => {
    const options = body
      ? {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      : {};
    const res = await fetch(url, options);
    return await res.json();
  };

  const calculate = async (mode = "auto", refresh = false) => {
  try {
    setError("");
    setLoading(true);

    if (mode === "save") {
      if (!vysledek) return;
      const data = await fetchData(`${API_URL}/ulozit_z_existujiciho/`, vysledek);
      if (data.error) setError(data.error);
      else alert("✅ Plán byl úspěšně uložen.");
      return;
    }

    if (mode === "load") {
      const data = await fetchData(`${API_URL}/ulozeny_plan/`);
      if (data.error) setError(data.error);
      else setVysledek(data);
      return;
    }

    // === Обновление плана с лимитом ===
    if (refresh) {
      if (refreshCount >= MAX_REFRESH_COUNT) {
        setError(`⚠️ Můžete obnovit plán maximálně ${MAX_REFRESH_COUNT}×.`);
        return;
      }
      setRefreshCount((c) => c + 1);
    }

    let body;

    if (mode === "manual") {
      if (!manualCalories) return setError("Zadejte kalorie ručně.");
      body = { manual_calories: manualCalories };
    } else {
      // Используем lastForm для обновления, если refresh = true
      const currentForm = refresh ? lastForm : form;

      if (!currentForm?.vaha || !currentForm?.vyska || !currentForm?.vek) {
        return setError("Vyplňte prosím všechny hodnoty.");
      }

      body = { ...currentForm };
    }

    body.refresh = refresh;

    const res = await fetch(`${API_URL}/vypocet/?_=${Date.now()}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (data.error) {
      setError(data.error);
    } else {
      setVysledek(data);
      setLastForm(form); // сохраняем последнюю форму
      if (mode === "auto" && !refresh) setRefreshCount(0); // сбросить счетчик при новом расчете
    }
  } catch (e) {
    console.error(e);
    setError("❌ Chyba při spojení s API.");
  } finally {
    setLoading(false);
  }
};

  const handleReturnToForm = () => {
    setVysledek(null);
    setForm(lastForm || INITIAL_FORM);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleClearAll = () => {
    setForm(INITIAL_FORM);
    setManualCalories("");
    setVysledek(null);
    setError("");
    setOpenIngredients({});
    setRefreshCount(0);
  };

  return (
    <div className="kalkulacka-container">
      <div className="kalkulacka-box">
        <h2>💪 Kalkulačka hubnutí</h2>

        {!vysledek && (
          <>
            <input type="number" name="vaha" placeholder="Váha (kg)" value={form.vaha} onChange={handleChange} />
            <input type="number" name="vyska" placeholder="Výška (cm)" value={form.vyska} onChange={handleChange} />
            <input type="number" name="vek" placeholder="Věk" value={form.vek} onChange={handleChange} />

            <select name="pohlavi" value={form.pohlavi} onChange={handleChange}>
              <option value="muz">Muž</option>
              <option value="zena">Žena</option>
            </select>

            <select name="aktivita" value={form.aktivita} onChange={handleChange}>
              <option value="sedavy">Sedavý režim</option>
              <option value="lehka">Lehká aktivita</option>
              <option value="stredni">Střední aktivita</option>
              <option value="vysoka">Vysoká aktivita</option>
              <option value="extra">Extra aktivita</option>
            </select>

            {/* === Кнопки === */}
            <button className="kalkulacka-button" onClick={() => calculate("auto")} disabled={loading}>
              📊 {loading ? "Počítám..." : "Spočítat podle údajů"}
            </button>
            <button
              className="kalkulacka-button"
              onClick={() => calculate("auto", true)}
              disabled={loading || refreshCount >= MAX_REFRESH_COUNT}
              style={{
                backgroundColor: refreshCount >= MAX_REFRESH_COUNT ? "#aaa" : "#f9a825",
              }}
            >
              🔄 Obnovit plán ({refreshCount}/{MAX_REFRESH_COUNT})
            </button>

            <div className="manual-section">
              <input
                type="number"
                value={manualCalories}
                onChange={(e) => setManualCalories(e.target.value)}
                placeholder="Zadejte kalorie ručně"
                className="manual-input"
              />
              <button
                className="kalkulacka-button"
                onClick={() => calculate("manual")}
                disabled={loading || !manualCalories}
              >
                ✏️ {loading ? "Počítám..." : "Spočítat ručně"}
              </button>
            </div>


            <button className="kalkulacka-button" onClick={() => calculate("save")} disabled={loading || !vysledek}>
              💾 Uložit plán
            </button>

            <button className="kalkulacka-button" onClick={() => calculate("load")} disabled={loading}>
              📋 Zobrazit uložený plán
            </button>
          </>
        )}

        {error && <p className="kalkulacka-error">{error}</p>}

        {vysledek && (
  <div className="kalkulacka-result">
    <h3>Doporučený denní příjem: {vysledek.details?.daily_target ?? "—"} kcal</h3>

    {dny.map((den) => {
      const denneJidla = vysledek.plan_data?.[den] || [];
      const dailyCalories = denneJidla.reduce(
        (sum, j) => sum + (Number(j.calories) || 0),
        0
      );

      return (
        <div key={den} className="denni-plan">
          <h4>
            {den.charAt(0).toUpperCase() + den.slice(1)} ({dailyCalories} kcal)
          </h4>
          <ul style={{ listStyle: "none", paddingLeft: 0 }}>
            {denneJidla.map((j, i) => (
              <li key={i} className="jidlo-item">
                <strong>{typyMap[j.type] ?? j.type}:</strong> {j.name} ({j.calories} kcal)
                {j.price && <span className="jidlo-price"> — {j.price} Kč</span>}

                {j.obrazek && (
 <img
  src={getImageUrl(j.obrazek)}  // j.obrazek = "8f078a4c.png"
  alt={j.name}
  className="jidlo-img"
  loading="lazy"
  onError={(e) => (e.target.src = `${MEDIA_URL}/fallback.jpg`)}
/>
)}
                {j.preparation && <p className="preparation">{j.preparation}</p>}

                {j.ingredients?.length > 0 && (
                  <>
                    <button
                      onClick={() => toggleIngredients(den, i)}
                      className="toggle-ingredients"
                    >
                      {openIngredients[`${den}-${i}`]
                        ? "🔽 Skrýt ingredience"
                        : "🔽 Zobrazit ingredience"}
                    </button>
                    {openIngredients[`${den}-${i}`] && (
                      <ul className="ingredients-list">
                        {j.ingredients.map((ing, idx) => (
                          <li key={idx}>
                            {ing.ingredient_name} – {ing.amount} {ing.unit}
                          </li>
                        ))}
                      </ul>
                    )}
                  </>
                )}
              </li>
            ))}
          </ul>
        </div>
      );
    })}

    {/* 🛒 Nákupní seznam */}
    {vysledek.shopping_list?.length > 0 && (
      <div className="nakupni-seznam">
        <h3>🛒 Nákupní seznam</h3>
        <ul style={{ listStyle: "none", paddingLeft: 0 }}>
          {vysledek.shopping_list.map((item, i) => (
            <li key={i}>
              {item.ingredient__name} – {item.total_amount} {item.ingredient__unit}
            </li>
          ))}
        </ul>
      </div>
    )}

    {/* 💾 КНОПКА СОХРАНЕНИЯ ПЕРЕНЕСЕНА СЮДА */}
    <div className="save-plan-box" style={{ marginTop: "20px" }}>
      <button
        className="kalkulacka-button"
        onClick={() => calculate("save")}
        disabled={loading || !vysledek}
        style={{ backgroundColor: "#1976d2", color: "#fff" }}
      >
        💾 Uložit plán
      </button>
    </div>

    {/* Кнопки управления */}
    <div className="result-actions">
      <button
        className="kalkulacka-button"
        onClick={handleReturnToForm}
        style={{ backgroundColor: "#4caf50", color: "#fff" }}
      >
        ← Zpět k formuláři
      </button>
      <button
        className="kalkulacka-button"
        onClick={handleClearAll}
        style={{ backgroundColor: "#9e9e9e", color: "#fff" }}
      >
        🧹 Vyčistit vše
      </button>
      
    </div>
  </div>
)}
      </div>
    </div>
  );
} 
