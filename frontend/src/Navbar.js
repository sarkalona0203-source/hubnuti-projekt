import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  return (
    <nav className="navbar">
      <Link className="nav-btn" to="/">Domů</Link>
      <Link className="nav-btn" to="/kalkulacka">Kalkulačka</Link>
      <Link className="nav-btn" to="/jidla">Jídla</Link>
      <Link className="nav-btn" to="/progress">Progress</Link>
    </nav>
  );
}