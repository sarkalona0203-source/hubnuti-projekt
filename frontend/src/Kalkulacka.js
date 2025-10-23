import React, { useState } from "react";
import "./kalkulacka.css";
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

function Kalkulacka() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [lastForm, setLastForm] = useState(null);
  const [manualCalories, setManualCalories] = useState("");
  const [vysledek, setVysledek] = useState(null);
  const [error, setError] = useState("");
  const [openIngredients, setOpenIngredients] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const toggleIngredients = (den, index) => {
    setOpenIngredients((prev) => ({
      ...prev,
      [`${den}-${index}`]: !prev[`${den}-${index}`],
    }));
  };

  const calculate = async (manual = false, refresh = false, loadSaved = false, save = false) => {
    try {
      setError("");
      setLoading(true);

      // 1. Сохранение текущего плана
      if (save && vysledek) {
        const res = await fetch("http://127.0.0.1:8000/api/ulozit_z_existujiciho/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(vysledek),
        });
        const data = await res.json();
        if (data.error) setError(data.error);
        else alert("Plán byl úspěšně uložen.");
        return;
      }

      // 2. Загрузка сохранённого плана
      if (loadSaved) {
        const res = await fetch("http://127.0.0.1:8000/api/ulozeny_plan/");
        const data = await res.json();
        if (data.error) setError(data.error);
        else setVysledek(data);
        return;
      }

      // 3. Новый расчёт
      let body = manual ? { manual_calories: manualCalories } : form;

      if (!manual && (!form.vaha || !form.vyska || !form.vek)) {
        setError("Vyplňte prosím všechny hodnoty.");
        return;
      }

      if (manual && !manualCalories) {
        setError("Zadejte hodnotu kalorií pro ruční výpočet.");
        return;
      }

      if (refresh) body.refresh = true;
      if (save) body.save = true;

      const res = await fetch("http://127.0.0.1:8000/api/vypocet/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setVysledek(data);
        setLastForm(form);
      }
    } catch (e) {
      console.error(e);
      setError("Chyba při spojení s API.");
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
    setVysledek(null);
    setForm(INITIAL_FORM);
    setManualCalories("");
    setError("");
    setLastForm(null);
    setOpenIngredients({});
  };

  return (
    <div className="kalkulacka-container">
      <div className="kalkulacka-box">
        <h2>Kalkulačka hubnutí</h2>

        {/* Formulář */}
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

        {/* Tlačítka */}
        <button className="kalkulacka-button" onClick={() => calculate(false)} disabled={loading}>
          📊 {loading ? "Počítám..." : "Spočítat podle údajů"}
        </button>

        <div className="manual-section">
          <input
            type="number"
            value={manualCalories}
            onChange={(e) => setManualCalories(e.target.value)}
            placeholder="Zadejte kalorie ručně"
            className="manual-input"
          />
          <button className="kalkulacka-button" onClick={() => calculate(true)} disabled={loading || !manualCalories}>
            ✏️ {loading ? "Počítám..." : "Spočítat ručně"}
          </button>
        </div>

        <button className="kalkulacka-button" onClick={() => calculate(false, true)} disabled={loading}>
          🔄 Obnovit plán
        </button>

        <button className="kalkulacka-button" onClick={() => calculate(false, false, false, true)} disabled={loading || !vysledek}>
          💾 Uložit plán
        </button>

        <button className="kalkulacka-button" onClick={() => calculate(false, false, true)} disabled={loading}>
          📋 Zobrazit uložený plán
        </button>

        {vysledek && (
          <>
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
              Vyčistit
            </button>
          </>
        )}

        {error && <p className="kalkulacka-error">{error}</p>}

        {/* Výsledek */}
        {vysledek && (
          <div className="kalkulacka-result">
            <h3>Doporučený denní příjem: {vysledek.details?.daily_target ?? "—"} kcal</h3>

            {dny.map((den) => {
              const denneJidla = vysledek.plan_data?.[den] || [];
              const dailyCalories = denneJidla.reduce((sum, j) => sum + (Number(j.calories) || 0), 0);

              return (
                <div key={den} className="denni-plan">
                  <h4>
                    {den.charAt(0).toUpperCase() + den.slice(1)} ({dailyCalories} kcal)
                  </h4>
                  <ul style={{ listStyle: "none", paddingLeft: 0 }}>
                    {denneJidla.map((j, i) => (
                      <li key={i} className="jidlo-item">
                        <strong>{typyMap[j.type] ?? j.type}:</strong> {j.name} ({j.calories} kcal)

                        {j.obrazek && (
                          <div className="jidlo-img-box">
                            <img
                              src={j.obrazek}
                              alt={j.name}
                              className="jidlo-img"
                              loading="lazy"
                              onError={(e) => {
                                e.target.onerror = null;
                                e.target.src = "/fallback.jpg"; // fallback image if needed
                              }}
                            />
                          </div>
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
                                    {ing.name} – {ing.amount} {ing.unit}
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
          </div>
        )}
      </div>
    </div>
  );
}

export default Kalkulacka;