import React from "react";
import "./HomePage.css";

export default function HomePage({ onStart }) {
  return (
    <div className="homepage-container">
      <div className="homepage-content">
        <h1 className="homepage-title">🍎 JidloApp – Váš osobní jídelní plán</h1>

        <p className="homepage-description">
          Vítejte v <strong>JidloApp!</strong>  
          Zde si můžete vytvořit svůj jídelní plán podle svých parametrů.  
          Kalkulačka vypočítá jídelníček s <strong>kalorickým deficitem 500 kcal denně</strong>.  
          To znamená, že můžete zhubnout přibližně <strong>0,5 kg za týden</strong> a  
          až <strong>2 kg za měsíc</strong> – bez hladovění!
        </p>

        <h2 className="homepage-subtitle">📋 Jak aplikaci používat:</h2>
        <ul className="homepage-list">
          <li>Zadejte své parametry – váhu, výšku, věk a úroveň aktivity.</li>
          <li>Klikněte na <strong>„Vypočítat plán“</strong>.</li>
          <li>Pokud vám jídelníček nevyhovuje, můžete ho aktualizovat až <strong>5×</strong>.</li>
          <li>Na konci se zobrazí <strong>seznam potravin pro nákup</strong>.</li>
          <li>Plán si můžete uložit a používat celý týden.</li>
        </ul>

        <h2 className="homepage-subtitle">💧 Důležité upozornění:</h2>
        <p className="homepage-text">
          Pijte dostatek vody! Pomáhá zrychlit metabolismus, snížit chuť k jídlu a zlepšit funkci těla.
          Káva, sladké nápoje nebo pivo mají vlastní kalorickou hodnotu, takže pokud je pijete,  
          snažte se o něco méně jíst.
        </p>

        <table className="water-table">
          <thead>
            <tr>
              <th>Váha (kg)</th>
              <th>Minimum (30 ml/kg)</th>
              <th>Optimální (40 ml/kg)</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>60</td><td>1.8 l</td><td>2.4 l</td></tr>
            <tr><td>70</td><td>2.1 l</td><td>2.8 l</td></tr>
            <tr><td>80</td><td>2.4 l</td><td>3.2 l</td></tr>
            <tr><td>90</td><td>2.7 l</td><td>3.6 l</td></tr>
            <tr><td>100</td><td>3.0 l</td><td>4.0 l</td></tr>
            <tr><td>120</td><td>3.6 l</td><td>4.8 l</td></tr>
            <tr><td>150</td><td>4.5 l</td><td>6.0 l</td></tr>
          </tbody>
        </table>

        <h2 className="homepage-subtitle">🥦 Další informace:</h2>
        <p className="homepage-text">
          Ovoce a zeleninu můžete měnit podle sezóny, hlavní je nezapomínat na zelené potraviny.  
          Na stránce výběru jídel uvidíte přibližnou cenu surovin i cenu hotového jídla.  
          Prémiová verze umožní sledovat vaši váhu a společně budeme sledovat pokroky.  
        </p>

        <p className="homepage-text">
          Pamatujte – váha se může někdy zastavit nebo mírně zvýšit.  
          To je přirozené, tělo není počítač. Buďte trpěliví ❤️  
          Společně to zvládneme – bez stresu, bez hladu, s úsměvem na výsledky!
        </p>
      </div>
    </div>
  );
}