import { useState } from "react";
import API from "../api";

export default function ProviderConfig() {
  const [provider, setProvider] = useState("exotel");
  const [form, setForm] = useState({});

  const save = async () => {
    await API.post("/admin/provider-config", {
      provider,
      ...form,
    });
    alert("Provider configuration saved");
  };

  return (
    <section className="card">
      <h2>Call Provider Configuration</h2>

      <div className="form-grid">
        <div>
          <label>Provider</label>
          <select value={provider} onChange={e => setProvider(e.target.value)}>
            <option value="exotel">Exotel</option>
            <option value="twilio">Twilio</option>
            <option value="plivo">Plivo</option>
          </select>
        </div>

        {provider === "exotel" && (
          <>
            <div>
              <label>Exotel SID</label>
              <input onChange={e => setForm({ ...form, sid: e.target.value })} />
            </div>
            <div>
              <label>API Key</label>
              <input onChange={e => setForm({ ...form, api_key: e.target.value })} />
            </div>
            <div>
              <label>Caller ID</label>
              <input placeholder="+91XXXXXXXXXX"
                onChange={e => setForm({ ...form, caller_id: e.target.value })} />
            </div>
          </>
        )}

        {provider === "twilio" && (
          <>
            <div>
              <label>Account SID</label>
              <input onChange={e => setForm({ ...form, sid: e.target.value })} />
            </div>
            <div>
              <label>Auth Token</label>
              <input type="password"
                onChange={e => setForm({ ...form, token: e.target.value })} />
            </div>
            <div>
              <label>From Number</label>
              <input placeholder="+1XXXXXXXXXX"
                onChange={e => setForm({ ...form, from: e.target.value })} />
            </div>
          </>
        )}

        {provider === "plivo" && (
          <>
            <div>
              <label>Auth ID</label>
              <input onChange={e => setForm({ ...form, auth_id: e.target.value })} />
            </div>
            <div>
              <label>Auth Token</label>
              <input type="password"
                onChange={e => setForm({ ...form, auth_token: e.target.value })} />
            </div>
            <div>
              <label>Caller ID</label>
              <input
                onChange={e => setForm({ ...form, caller_id: e.target.value })} />
            </div>
          </>
        )}
      </div>

      <button className="primary-btn" onClick={save}>
        Save Provider Configuration
      </button>
    </section>
  );
}
