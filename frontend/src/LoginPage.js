import React, { useState } from "react";
import { useAuth } from "./AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // очищаем предыдущие ошибки

    try {
      const success = await login(username.trim(), password.trim());
      if (!success) {
        setError("Neplatné uživatelské jméno nebo heslo");
      }
    } catch (err) {
      setError("Chyba při přihlášení. Zkuste to prosím znovu.");
      console.error(err);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Přihlášení</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="text"
          placeholder="Uživatelské jméno"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={styles.input}
          required
        />
        <input
          type="password"
          placeholder="Heslo"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
          required
        />
        <button type="submit" style={styles.button}>
          Přihlásit se
        </button>
      </form>
      {error && <p style={styles.error}>{error}</p>}
    </div>
  );
}

const styles = {
  container: {
    textAlign: "center",
    marginTop: "100px",
  },
  form: {
    display: "inline-block",
    textAlign: "left",
  },
  input: {
    display: "block",
    width: "250px",
    padding: "8px",
    marginBottom: "10px",
    fontSize: "14px",
  },
  button: {
    width: "100%",
    padding: "10px",
    fontSize: "16px",
    cursor: "pointer",
  },
  error: {
    color: "red",
    marginTop: "10px",
  },
};