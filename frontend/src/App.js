import React from "react";
import Kalkulacka from "./Kalkulacka";
import './kalkulacka.css';

function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundImage: 'url("images/brooke-lark-08bOYnH_r_E-unsplash.jpg")',
        backgroundPosition: "center",
        backgroundSize: "cover",
        backgroundRepeat: "no-repeat",
        // fontFamily: "Arial", // убрать
      }}
    >
      <Kalkulacka />
    </div>
  );
}

export default App;