import { useState } from "react";
import API from "../api";

export default function AddChallan({ onSuccess }) {
  const [form, setForm] = useState({
    name: "",
    phone: "",
    language: "english",
    challan_type: "Over Speeding",
    amount: 700,
    last_date: "",
    late_fee_type: "Fixed",
    late_fee: 50,
  });

  const update = (k, v) => setForm({ ...form, [k]: v });

    const submit = async () => {
      // 🔒 PHONE VALIDATION (PASTE HERE)
      if (form.phone.length !== 10) {
        alert("Enter a valid 10-digit Indian mobile number");
        return;
      }
    
      await API.post("/challan", form);
      onSuccess();
    };


  return (
    <section className="card">
      <h2>Add New Challan</h2>

      <div className="form-grid">
        <div>
          <label>Name</label>
          <input value={form.name} onChange={e => update("name", e.target.value)} />
        </div>

        <div>
          <label>Phone (+91)</label>
          <input
            placeholder="+91 XXXXXXXXXX"
            value={form.phone ? `+91 ${form.phone}` : ""}
            onChange={e => {
              const value = e.target.value.replace(/\D/g, "");
              if (value.length <= 10) {
                update("phone", value);
              }
            }}
          />
          {form.phone && form.phone.length !== 10 && (
            <span className="error">Enter valid 10-digit Indian number</span>
          )}
        </div>


        <div>
          <label>Language</label>
          <select value={form.language} onChange={e => update("language", e.target.value)}>
            <option value="english">English</option>
            <option value="hindi">Hindi</option>
            <option value="marathi">Marathi</option>
          </select>
        </div>

        <div>
          <label>Challan Type</label>
          <select value={form.challan_type} onChange={e => update("challan_type", e.target.value)}>
            <option>Over Speeding</option>
            <option>No Helmet</option>
            <option>No Seatbelt</option>
            <option>Signal Jump</option>
          </select>
        </div>

        <div>
          <label>Amount (₹)</label>
          <input type="number" value={form.amount}
            onChange={e => update("amount", e.target.value)} />
        </div>

        <div>
          <label>Last Date</label>
          <input type="date" value={form.last_date}
            onChange={e => update("last_date", e.target.value)} />
        </div>

        <div>
          <label>Late Fee Type</label>
          <select value={form.late_fee_type}
            onChange={e => update("late_fee_type", e.target.value)}>
            <option>Fixed</option>
            <option>Per Day</option>
          </select>
        </div>

        <div>
          <label>Late Fee (₹)</label>
          <input type="number" value={form.late_fee}
            onChange={e => update("late_fee", e.target.value)} />
        </div>
      </div>

      <button className="primary-btn" onClick={submit}>
        Submit Challan
      </button>
    </section>
  );
}
