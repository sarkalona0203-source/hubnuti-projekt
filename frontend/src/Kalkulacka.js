import React, { useState } from "react";
import "./kalkulacka.css";

function Kalkulacka() {
  const [form, setForm] = useState({
    vaha: "",
    vyska: "",
    vek: "",
    pohlavi: "muz",
    aktivita: "sedavy",
  });

  const [manualCalories, setManualCalories] = useState("");
  const [vysledek, setVysledek] = useState(null);
  const [error, setError] = useState("");

  const dny = ["pondeli", "utery", "streda", "ctvrtek", "patek", "sobota", "nedele"];
  const jidla = [
    { key: "snidane", label: "Snídaně" },
    { key: "druhe_snidane", label: "Druhá snídaně" },
    { key: "svacina", label: "Svačina" },
    { key: "obed", label: "Oběd" },
    { key: "vecere", label: "Večeře" },
  ];

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const handleManualChange = (e) => setManualCalories(e.target.value);

  const calculate = async (manual = false) => {
    try {
      let body = manual ? { manual_calories: manualCalories } : form;

      if (manual && !manualCalories) {
        setError("Zadejte hodnotu kalorií pro ruční výpočet");
        return;
      }

      const res = await fetch("http://127.0.0.1:8000/api/vypocet/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (data.error) {
        setError(data.error);
        setVysledek(null);
      } else {
        setVysledek(data);
        setError("");
      }
    } catch {
      setError("Chyba při spojení s API");
      setVysledek(null);
    }
  };

  return (
    <div className="kalkulacka-container">
      <div className="kalkulacka-box">
        <h2>Kalkulačka hubnutí</h2>

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

        <button className="kalkulacka-button" onClick={() => calculate(false)}>Spočítat podle údajů</button>

        <input type="number" placeholder="Kalorie ručně" value={manualCalories} onChange={handleManualChange} />
        <button className="kalkulacka-button" onClick={() => calculate(true)}>Spočítat ručně</button>

        {error && <p className="kalkulacka-error">{error}</p>}

        {vysledek && (
          <div className="kalkulacka-result">
            <h3>Doporučený denní příjem: {vysledek.kalorie?.Plan_celkem || vysledek.kalorie?.Deficit_500 || vysledek.kalorie?.TDEE} kcal</h3>

            {dny.map((den) => {
              const denneJidla = vysledek.plan?.[den] || [];
              const dailyCalories = denneJidla.reduce((sum, j) => sum + (j.calories || 0), 0);

              return (
                <div key={den} style={{ marginBottom: "20px" }}>
                  <h4>{den.charAt(0).toUpperCase() + den.slice(1)} ({dailyCalories} kcal)</h4>
                  <ul style={{ listStyle: "none", paddingLeft: 0 }}>
                    {denneJidla.map((j) => (
                      <li key={j.typ}>
                        <strong>{j.typ}:</strong> {j.name} ({j.calories} kcal)
                        {j.ingredients?.length > 0 && (
                          <ul>
                            {j.ingredients.map((ing, idx) => (
                              <li key={idx}>{ing.ingredient_name}: {ing.amount} {ing.unit}</li>
                            ))}
                          </ul>
                        )}
                        {j.preparation && <p>🍳 {j.preparation}</p>}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}

            {vysledek.nakupni_seznam && (
              <div className="kalkulacka-shopping-list">
                <h3>🛒 Nákupní seznam</h3>
                <ul>
                  {vysledek.nakupni_seznam.map((item, idx) => (
                    <li key={idx}>
                      {item.ingredient__name}: {item.total_amount} {item.ingredient__unit}
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