import { useState } from "react";
import API from "../api";

export default function AdminPanel({ onBack }) {
  const [form, setForm] = useState({
    account_sid: "",
    auth_token: "",
    phone_number: "",
  });

  const save = async () => {
    await API.post("/admin/twilio-config", form);
    onBack();
  };

  return (
    <section className="card">
      <h2>Admin – Twilio Configuration</h2>

      <div className="form-grid">
        <div>
          <label>Account SID</label>
          <input onChange={e => setForm({ ...form, account_sid: e.target.value })} />
        </div>

        <div>
          <label>Auth Token</label>
          <input type="password"
            onChange={e => setForm({ ...form, auth_token: e.target.value })} />
        </div>

        <div>
          <label>Phone Number</label>
          <input placeholder="+1XXXXXXXXXX"
            onChange={e => setForm({ ...form, phone_number: e.target.value })} />
        </div>
      </div>

      <div style={{ display: "flex", gap: 12 }}>
        <button className="primary-btn" onClick={save}>Save Twilio Settings</button>
        <button className="secondary-btn" onClick={onBack}>Back</button>
      </div>
    </section>
  );
}
