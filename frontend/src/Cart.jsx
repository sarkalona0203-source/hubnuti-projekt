import React from "react";
import { getImageUrl } from "./config"; // 🔥 добавляем

export default function Cart({ cart, onRemove, deliveryFee = 0 }) {
  const total = cart.reduce(
    (sum, item) => sum + (Number(item.readyPrice) || 0) * (Number(item.quantity) || 0),
    0
  );

  const totalWithDelivery = total + deliveryFee;

  if (!cart.length) return null;

  return (
    <div className="cart-box bg-white rounded-xl shadow-lg p-4 mt-6">
      <h2 className="font-bold text-lg">🛍️ Košík ({cart.length} položek)</h2>
      <ul>
        {cart.map(item => (
          <li key={item.id} className="flex justify-between py-1 items-center">
            <img
              src={getImageUrl(item.image)} // 🔥 используем getImageUrl
              alt={item.name}
              style={{ width: 60, height: 60, borderRadius: 5, objectFit: "cover" }}
              onError={(e) => { e.currentTarget.onerror = null; e.currentTarget.style.display = "none"; }} // скрывать если не загрузилось
            />
            <div>
              <div>
                {item.name} × {item.quantity}
              </div>
              <div className="text-xs text-gray-600">
                Hotové jídlo: {item.readyPrice} Kč / ks
              </div>
            </div>
            <div>
              {(item.readyPrice * item.quantity).toFixed(2)} Kč
              <button
                className="ml-2 text-red-500"
                onClick={() => onRemove(item.id)}
              >
                ✖
              </button>
            </div>
          </li>
        ))}
      </ul>

      <div className="cart-total font-bold mt-2">
        Součet jídel: {total.toFixed(2)} Kč <br />
        Doprava: {deliveryFee} Kč <br />
        Celkem k úhradě: {totalWithDelivery.toFixed(2)} Kč
      </div>
    </div>
  );
}