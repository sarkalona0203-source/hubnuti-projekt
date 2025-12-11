import React, { useState } from "react";
import "./JidlaPage.css";
import { MEDIA_URL, getImageUrl } from "./config";



export default function JidloCard({ jidlo, onAdd }) {
  const types = jidlo.types || [];
  const prices = jidlo.prices || {};
  const defaultType = types[0] || "";
  const [selectedType, setSelectedType] = useState(defaultType);


  const normalPrice = types.length ? prices[selectedType] || 0 : jidlo.price_value || 0;
  const readyPrice = jidlo.ready_price_value || 0;

  const handleAddClick = () => {
    onAdd(jidlo, selectedType, normalPrice, readyPrice);
  };

  // === Правильное построение URL картинки ===
  const imgSrc = getImageUrl(jidlo.obrazek);

  return (
    <div className="jidlo-card card">
      <img
  src={getImageUrl(jidlo.obrazek)}
  alt={jidlo.name}
  style={{ width: "200px", border: "1px solid red" }}
  onError={(e) => (e.target.src = `${MEDIA_URL}/fallback.jpg`)}
/>

      <h3 className="jidlo-title">{jidlo.name}</h3>
      {jidlo.description && <p>{jidlo.description}</p>}

      <div className="jidlo-info">
        {jidlo.protein && <p>Bílkoviny: {jidlo.protein} g</p>}
        {jidlo.calories && <p>Kalorie: {jidlo.calories} kcal</p>}
      </div>

      {types.length > 0 && (
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
        >
          {types.map((type) => (
            <option key={type} value={type}>
              {type} — {prices[type] || 0} Kč
            </option>
          ))}
        </select>
      )}

      <div style={{ marginTop: "8px", fontWeight: "bold" }}>
        Cena surovin: {Number(normalPrice).toFixed(2)} Kč | Cena hotového jídla:{" "}
        {Number(readyPrice).toFixed(2)} Kč
      </div>

      <button className="kalkulacka-button mt-2" onClick={handleAddClick}>
        ➕ Přidat do košíku
      </button>
    </div>
  );
}
