import React, { useEffect, useState } from "react";
import Filters from "./Filters";
import JidloCard from "./JidloCard";
import Cart from "./Cart";
import "./JidlaPage.css";

export default function JidlaPage() {
  const [jidla, setJidla] = useState([]);
  const [filters, setFilters] = useState({});
  const [cart, setCart] = useState([]);
  const DELIVERY_FEE = 100;

  // Fetch jídel
  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });

    const url = `http://127.0.0.1:8000/api/vsechna_jidla/?${params.toString()}`;
    fetch(url)
      .then(res => res.json())
      .then(setJidla)
      .catch(err => console.error(err));
  }, [filters]);

  const handleAddToCart = (jidlo, type, price, readyPrice) => {
  const id = `${jidlo.id}-${type}`;
  const existing = cart.find(item => item.id === id);

  // ✅ преобразуем строковые значения в числа
  const numericPrice = Number(price).toFixed(2);
  const numericReadyPrice = Number(readyPrice).toFixed(2);
  if (existing) {
    setCart(cart.map(item =>
      item.id === id
        ? { ...item, quantity: item.quantity + 1 }
        : item
    ));
  } else {
    setCart([...cart, {
      id,
      name: jidlo.name,
      type,
      price: numericPrice,
      readyPrice: numericReadyPrice,
      quantity: 1, // 🔹 добавим поле quantity, чтобы считать правильно
      protein: jidlo.protein,
      calories: jidlo.calories,
      image: jidlo.obrazek?.startsWith("http")
        ? jidlo.obrazek
        : `http://127.0.0.1:8000${jidlo.obrazek || "/images/placeholder.png"}`
    }]);
  }
};

  const handleRemoveFromCart = (id) => {
    setCart(prev => prev.filter(item => item.id !== id));
  };

  return (
    <div className="page-container">
      <h1 className="page-title">🍽️ Seznam jídel</h1>

      <div className="filters-container">
        <Filters onChange={setFilters} />
      </div>

      <div className="jidla-grid">
        {jidla.map(j => (
          <JidloCard key={j.id} jidlo={j} onAdd={handleAddToCart} />
        ))}
      </div>

      {cart.length > 0 && (
        <Cart cart={cart} onRemove={handleRemoveFromCart} deliveryFee={DELIVERY_FEE} />
      )}
    </div>
  );
}