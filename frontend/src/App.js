import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Kalkulacka from "./Kalkulacka";
import JidlaPage from "./JidlaPage";
import HomePage from "./HomePage";
import PristupPremium from "./PristupPremium";
import Navbar from "./Navbar"; // компонент навигации
import "./App.css";

export default function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/kalkulacka" element={<Kalkulacka />} />
        <Route path="/jidla" element={<JidlaPage />} />
        <Route path="/progress" element={<PristupPremium />} />
      </Routes>
    </Router>
  );
}