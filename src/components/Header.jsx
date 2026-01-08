export default function Header() {
  return (
    <>
      {/* GOVERNMENT STRIP */}
      <div className="gov-strip">
        <div className="gov-left">
          <img
            src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg"
            alt="State Emblem"
          />
          <span>Government of Maharashtra</span>
        </div>

        <div className="gov-right">
          <span>English</span>
          <span className="divider">|</span>
          <span>हिंदी</span>
          <span className="divider">|</span>
          <span>मराठी</span>
        </div>
      </div>

      {/* MAIN HEADER */}
      <header className="main-header">
        <h1>Maharashtra Traffic Challan Reminder System</h1>
        <p>Transport Department, Government of Maharashtra</p>
        <span className="location-tag">Maharashtra, India</span>
      </header>

      {/* NAVIGATION BAR */}
      <nav className="gov-nav">
        <ul>
          <li className="active">Home</li>
          <li>Challan Dashboard</li>
          <li>Bulk Operations</li>
          <li>Reports</li>
          <li>Admin</li>
        </ul>
      </nav>
    </>
  );
}
