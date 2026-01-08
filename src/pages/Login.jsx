import { useState } from "react";
import "../App.css";

const USERNAME = "mh_admin";
const PASSWORD = "mh@2026";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = () => {
    if (username === USERNAME && password === PASSWORD) {
      localStorage.setItem("loggedIn", "true");
      onLogin();
    } else {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Maharashtra Traffic Challan System</h1>
        <p>Government of Maharashtra</p>

        <div className="form-group">
          <label>Username</label>
          <input onChange={e => setUsername(e.target.value)} />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input type="password" onChange={e => setPassword(e.target.value)} />
        </div>

        {error && <div className="error">{error}</div>}

        <button className="primary-btn" onClick={handleLogin}>
          Login
        </button>
      </div>
    </div>
  );
}
