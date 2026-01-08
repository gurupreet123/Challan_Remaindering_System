import { useState } from "react";
import API from "../api";

export default function CsvUpload({ onSuccess }) {
  const [file, setFile] = useState(null);

  const upload = async () => {
    if (!file) {
      alert("Please select a CSV file");
      return;
    }
    const fd = new FormData();
    fd.append("file", file);
    await API.post("/upload-csv", fd);
    onSuccess();
  };

  return (
    <section className="card">
      <h2>Bulk Upload via CSV</h2>

      {/* CSV REQUIREMENTS */}
      <div className="hint">
        <strong>CSV Requirements:</strong>
        <ul>
          <li>Phone number must be 10 digits (without +91)</li>
          <li>Date format: YYYY-MM-DD</li>
          <li>Language: english / hindi / marathi</li>
          <li>Late Fee Type: Fixed or Per Day</li>
        </ul>
      </div>

      {/* DOWNLOAD SAMPLE */}
      <div className="csv-download">
        <a
          href="/sample_challan.csv"
          download
          className="download-btn"
        >
          📥 Download Sample CSV
        </a>
      </div>

      {/* UPLOAD */}
      <div className="csv-upload">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button className="secondary-btn" onClick={upload}>
          Upload CSV
        </button>
      </div>
    </section>
  );
}
