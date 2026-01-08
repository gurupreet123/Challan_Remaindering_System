export default function Dashboard() {
  return (
    <section className="dashboard">
      <div className="dash-card">
        <h3>Total Challans</h3>
        <p>System Generated</p>
        <span>—</span>
      </div>

      <div className="dash-card">
        <h3>Calls Today</h3>
        <p>Automated Voice Calls</p>
        <span>12:00 – 18:00</span>
      </div>

      <div className="dash-card">
        <h3>Pending Calls</h3>
        <p>Awaiting Delivery</p>
        <span>Retry Enabled</span>
      </div>

      <div className="dash-card">
        <h3>Languages Supported</h3>
        <p>Voice Notification</p>
        <span>English | हिंदी | मराठी</span>
      </div>
    </section>
  );
}
