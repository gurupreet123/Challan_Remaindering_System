import { useEffect, useState } from "react";
import API from "../api";

export default function ChallanList() {
  const [data, setData] = useState([]);

  const load = async () => {
    const res = await API.get("/challans");
    setData(res.data); // 🔥 latest first
  };

    useEffect(() => {
      const fetchData = () => {
        API.get("/challans")
          .then(res => setData(res.data))
          .catch(() => {});
      };
    
      fetchData(); // initial load
    
      const interval = setInterval(fetchData, 2000); // ⏱ every 2 sec
    
      return () => clearInterval(interval); // cleanup
    }, []);


  return (
    <section className="card">
      <h2>Challan Records</h2>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Language</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Attempts</th>
              <th>Last Duration</th>
              <th>Listen</th>
            </tr>
          </thead>

          <tbody>
            {data.map((c, i) => (
              <tr key={i}>
                <td>{c.name}</td>
                <td>{c.phone}</td>
                <td>{c.language}</td>
                <td>{c.challan_type || "Over Speeding"}</td>
                <td>₹{c.amount}</td>

                <td className={`status ${c.status}`}>
                  {c.status}
                </td>

                <td>{c.call_attempts}</td>
                <td>{c.last_duration ? `${c.last_duration}s` : "-"}</td>

                <td className={`listen ${c.listen_status || "pending"}`}>
                  {c.listen_status || "waiting"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
