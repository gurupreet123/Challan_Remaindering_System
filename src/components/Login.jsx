import { useState } from "react";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = () => {
    if (username === "admin_maha" && password === "challan@123") {
      onLogin();
    } else {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h2>Government of Maharashtra</h2>
        <p className="subtext">
          Maharashtra Traffic Challan Reminder System
        </p>

        <div className="login-group">
          <label>Username</label>
          <input
            placeholder="Enter Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div className="login-group">
          <label>Password</label>
          <input
            type="password"
            placeholder="Enter Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {error && <div className="error">{error}</div>}

        <button className="primary-btn" onClick={submit}>
          Login
        </button>

        <p className="login-footer">
          © Government of Maharashtra – Transport Department
        </p>
      </div>
    </div>
  );
}
