import { useState } from "react";
import Header from "./components/Header";
import Login from "./components/Login";
import AddChallan from "./components/AddChallan";
import CsvUpload from "./components/CsvUpload";
import ChallanList from "./components/ChallanList";
import Announcement from "./components/Announcement";
import Dashboard from "./components/Dashboard";
import "./App.css";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [refresh, setRefresh] = useState(0);

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  return (
    <div className="page">
      <Header />
      <Announcement />
      <Dashboard />
      <AddChallan onSuccess={() => setRefresh(refresh + 1)} />
      <CsvUpload onSuccess={() => setRefresh(refresh + 1)} />
      <ChallanList key={refresh} />
    </div>
  );
}
