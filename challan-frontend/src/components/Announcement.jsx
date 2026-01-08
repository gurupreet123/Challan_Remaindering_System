export default function Announcement() {
  return (
    <div className="announcement">
      <marquee behavior="scroll" direction="left">
        🔔 Important Notice: Automated challan reminder calls are placed only between
        12:00 PM and 6:00 PM. Please ensure correct mobile numbers and language
        selection while entering challan details. This system is for official use
        by the Transport Department, Government of Maharashtra.
      </marquee>
    </div>
  );
}
