import React, { useState } from "react";
import "./JidlaPage.css";

export default function Filters({ onChange }) {
  const [filters, setFilters] = useState({
    minPrice: "",
    maxPrice: "",
    minReadyPrice: "",
    maxReadyPrice: "",
    minProtein: "",
    maxProtein: "",
    minCalories: "",
    maxCalories: "",
    category: "",
  });

  const mapping = {
    minPrice: "product_price__gte",
    maxPrice: "product_price__lte",
    minReadyPrice: "ready_price__gte",
    maxReadyPrice: "ready_price__lte",
    minProtein: "protein__gte",
    maxProtein: "protein__lte",
    minCalories: "calories__gte",
    maxCalories: "calories__lte",
    category: "category",
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    const newFilters = { ...filters, [name]: value };
    setFilters(newFilters);

    const mappedFilters = Object.fromEntries(
      Object.entries(newFilters)
        .filter(([_, val]) => val !== "")
        .map(([key, val]) => [mapping[key] || key, val])
    );

    onChange(mappedFilters);
  };

  return (
    <div className="filters-container">
      <input
        name="minPrice"
        placeholder="Cena surovin ot (Kč)"
        value={filters.minPrice}
        onChange={handleChange}
      />
      <input
        name="maxPrice"
        placeholder="Cena surovin do (Kč)"
        value={filters.maxPrice}
        onChange={handleChange}
      />
      <input
        name="minReadyPrice"
        placeholder="Cena hotového jídla od (Kč)"
        value={filters.minReadyPrice}
        onChange={handleChange}
      />
      <input
        name="maxReadyPrice"
        placeholder="Cena hotového jídla do (Kč)"
        value={filters.maxReadyPrice}
        onChange={handleChange}
      />
      <input
        name="minProtein"
        placeholder="Bílkoviny od"
        value={filters.minProtein}
        onChange={handleChange}
      />
      <input
        name="maxProtein"
        placeholder="Bílkoviny do"
        value={filters.maxProtein}
        onChange={handleChange}
      />
      <input
        name="minCalories"
        placeholder="Kalorie od"
        value={filters.minCalories}
        onChange={handleChange}
      />
      <input
        name="maxCalories"
        placeholder="Kalorie do"
        value={filters.maxCalories}
        onChange={handleChange}
      />
      <select name="category" value={filters.category} onChange={handleChange}>
        <option value="">Všechny kategorie</option>
        <option value="snidane">Snídaně</option>
        <option value="obed">Oběd</option>
        <option value="vecere">Večeře</option>
      </select>
    </div>
  );
}