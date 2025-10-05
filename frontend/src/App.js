import React from "react";
import Kalkulacka from "./Kalkulacka";

function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundImage: `url("/images/brooke-lark-nTZOILVZuOg-unsplash.jpg")`,
        backgroundPosition: "center",
        backgroundSize: "cover",
        backgroundRepeat: "no-repeat",
        fontFamily: "Arial",
      }}
    >
      <Kalkulacka />
    </div>
  );
}

export default App;